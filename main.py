# Import các thư viện cần thiết
import os
import re
import sys
from pathlib import Path
import yaml
import click
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from lib_resume_builder_AIHawk import Resume,StyleManager,FacadeManager,ResumeGenerator
from src.utils import chrome_browser_options
from src.llm.llm_manager import GPTAnswerer
from src.aihawk_authenticator import AIHawkAuthenticator
from src.aihawk_bot_facade import AIHawkBotFacade
from src.aihawk_job_manager import AIHawkJobManager
from src.job_application_profile import JobApplicationProfile
from loguru import logger

# Tắt các thông báo lỗi tiêu chuẩn
sys.stderr = open(os.devnull, 'w')

# Định nghĩa lớp ngoại lệ tùy chỉnh cho lỗi cấu hình
class ConfigError(Exception):
    pass

# Lớp để xác thực cấu hình
class ConfigValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        # Kiểm tra tính hợp lệ của địa chỉ email
        return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None
    
    @staticmethod
    def validate_yaml_file(yaml_path: Path) -> dict:
        # Đọc và xác thực file YAML
        try:
            with open(yaml_path, 'r') as stream:
                return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise ConfigError(f"Lỗi khi đọc file {yaml_path}: {exc}")
        except FileNotFoundError:
            raise ConfigError(f"Không tìm thấy file: {yaml_path}")
    
    @staticmethod
    def validate_config(config_yaml_path: Path) -> dict:
        # Xác thực file cấu hình
        parameters = ConfigValidator.validate_yaml_file(config_yaml_path)
        required_keys = {
            'remote': bool,
            'experienceLevel': dict,
            'jobTypes': dict,
            'date': dict,
            'positions': list,
            'locations': list,
            'distance': int,
            'companyBlacklist': list,
            'titleBlacklist': list,
            'llm_model_type': str,
            'llm_model': str
        }

        # Kiểm tra các khóa bắt buộc và kiểu dữ liệu
        for key, expected_type in required_keys.items():
            if key not in parameters:
                if key in ['companyBlacklist', 'titleBlacklist']:
                    parameters[key] = []
                else:
                    raise ConfigError(f"Thiếu hoặc không hợp lệ khóa '{key}' trong file cấu hình {config_yaml_path}")
            elif not isinstance(parameters[key], expected_type):
                if key in ['companyBlacklist', 'titleBlacklist'] and parameters[key] is None:
                    parameters[key] = []
                else:
                    raise ConfigError(f"Kiểu không hợp lệ cho khóa '{key}' trong file cấu hình {config_yaml_path}. Cần {expected_type}.")

        # Kiểm tra các cấp độ kinh nghiệm
        experience_levels = ['internship', 'entry', 'associate', 'mid-senior level', 'director', 'executive']
        for level in experience_levels:
            if not isinstance(parameters['experienceLevel'].get(level), bool):
                raise ConfigError(f"Cấp độ kinh nghiệm '{level}' phải là boolean trong file cấu hình {config_yaml_path}")

        # Kiểm tra các loại công việc
        job_types = ['full-time', 'contract', 'part-time', 'temporary', 'internship', 'other', 'volunteer']
        for job_type in job_types:
            if not isinstance(parameters['jobTypes'].get(job_type), bool):
                raise ConfigError(f"Loại công việc '{job_type}' phải là boolean trong file cấu hình {config_yaml_path}")

        # Kiểm tra các bộ lọc ngày
        date_filters = ['all time', 'month', 'week', '24 hours']
        for date_filter in date_filters:
            if not isinstance(parameters['date'].get(date_filter), bool):
                raise ConfigError(f"Bộ lọc ngày '{date_filter}' phải là boolean trong file cấu hình {config_yaml_path}")

        # Kiểm tra danh sách vị trí và địa điểm
        if not all(isinstance(pos, str) for pos in parameters['positions']):
            raise ConfigError(f"'positions' phải là danh sách các chuỗi trong file cấu hình {config_yaml_path}")
        if not all(isinstance(loc, str) for loc in parameters['locations']):
            raise ConfigError(f"'locations' phải là danh sách các chuỗi trong file cấu hình {config_yaml_path}")

        # Kiểm tra khoảng cách
        approved_distances = {0, 5, 10, 25, 50, 100}
        if parameters['distance'] not in approved_distances:
            raise ConfigError(f"Giá trị khoảng cách không hợp lệ trong file cấu hình {config_yaml_path}. Phải là một trong: {approved_distances}")

        # Kiểm tra danh sách đen
        for blacklist in ['companyBlacklist', 'titleBlacklist']:
            if not isinstance(parameters.get(blacklist), list):
                raise ConfigError(f"'{blacklist}' phải là danh sách trong file cấu hình {config_yaml_path}")
            if parameters[blacklist] is None:
                parameters[blacklist] = []

        return parameters

    @staticmethod
    def validate_secrets(secrets_yaml_path: Path) -> tuple:
        # Xác thực file bí mật
        secrets = ConfigValidator.validate_yaml_file(secrets_yaml_path)
        mandatory_secrets = ['llm_api_key']

        for secret in mandatory_secrets:
            if secret not in secrets:
                raise ConfigError(f"Thiếu bí mật '{secret}' trong file {secrets_yaml_path}")

        if not secrets['llm_api_key']:
            raise ConfigError(f"llm_api_key không thể trống trong file bí mật {secrets_yaml_path}.")
        return secrets['llm_api_key']

# Lớp quản lý file
class FileManager:
    @staticmethod
    def find_file(name_containing: str, with_extension: str, at_path: Path) -> Path:
        # Tìm file dựa trên tên và phần mở rộng
        return next((file for file in at_path.iterdir() if name_containing.lower() in file.name.lower() and file.suffix.lower() == with_extension.lower()), None)

    @staticmethod
    def validate_data_folder(app_data_folder: Path) -> tuple:
        # Xác thực thư mục dữ liệu
        if not app_data_folder.exists() or not app_data_folder.is_dir():
            raise FileNotFoundError(f"Không tìm thấy thư mục dữ liệu: {app_data_folder}")

        required_files = ['secrets.yaml', 'config.yaml', 'plain_text_resume.yaml']
        missing_files = [file for file in required_files if not (app_data_folder / file).exists()]
        
        if missing_files:
            raise FileNotFoundError(f"Thiếu các file trong thư mục dữ liệu: {', '.join(missing_files)}")

        output_folder = app_data_folder / 'output'
        output_folder.mkdir(exist_ok=True)
        return (app_data_folder / 'secrets.yaml', app_data_folder / 'config.yaml', app_data_folder / 'plain_text_resume.yaml', output_folder)

    @staticmethod
    def file_paths_to_dict(resume_file: Path | None, plain_text_resume_file: Path) -> dict:
        # Chuyển đổi đường dẫn file thành từ điển
        if not plain_text_resume_file.exists():
            raise FileNotFoundError(f"Không tìm thấy file sơ yếu lý lịch văn bản thuần: {plain_text_resume_file}")

        result = {'plainTextResume': plain_text_resume_file}

        if resume_file:
            if not resume_file.exists():
                raise FileNotFoundError(f"Không tìm thấy file sơ yếu lý lịch: {resume_file}")
            result['resume'] = resume_file

        return result

def init_browser() -> webdriver.Chrome:
    # Khởi tạo trình duyệt Chrome
    try:
        options = chrome_browser_options()
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    except Exception as e:
        raise RuntimeError(f"Không thể khởi tạo trình duyệt: {str(e)}")

def create_and_run_bot(parameters, llm_api_key):
    # Tạo và chạy bot
    try:
        # Khởi tạo các thành phần cần thiết
        style_manager = StyleManager()
        resume_generator = ResumeGenerator()
        with open(parameters['uploads']['plainTextResume'], "r", encoding='utf-8') as file:
            plain_text_resume = file.read()
        resume_object = Resume(plain_text_resume)
        resume_generator_manager = FacadeManager(llm_api_key, style_manager, resume_generator, resume_object, Path("data_folder/output"))
        os.system('cls' if os.name == 'nt' else 'clear')
        resume_generator_manager.choose_style()
        os.system('cls' if os.name == 'nt' else 'clear')
        
        job_application_profile_object = JobApplicationProfile(plain_text_resume)
        
        # Khởi tạo trình duyệt và các thành phần bot
        browser = init_browser()
        login_component = AIHawkAuthenticator(browser)
        apply_component = AIHawkJobManager(browser)
        gpt_answerer_component = GPTAnswerer(parameters, llm_api_key)
        bot = AIHawkBotFacade(login_component, apply_component)
        bot.set_job_application_profile_and_resume(job_application_profile_object, resume_object)
        bot.set_gpt_answerer_and_resume_generator(gpt_answerer_component, resume_generator_manager)
        bot.set_parameters(parameters)
        bot.start_login()
        bot.start_apply()
    except WebDriverException as e:
        logger.error(f"Lỗi WebDriver xảy ra: {e}")
    except Exception as e:
        raise RuntimeError(f"Lỗi khi chạy bot: {str(e)}")

@click.command()
@click.option('--resume', type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path), help="Đường dẫn đến file PDF sơ yếu lý lịch")
def main(resume: Path = None):
    # Hàm chính của chương trình
    try:
        # Xác thực và chuẩn bị dữ liệu
        data_folder = Path("data_folder")
        secrets_file, config_file, plain_text_resume_file, output_folder = FileManager.validate_data_folder(data_folder)
        
        parameters = ConfigValidator.validate_config(config_file)
        llm_api_key = ConfigValidator.validate_secrets(secrets_file)
        
        parameters['uploads'] = FileManager.file_paths_to_dict(resume, plain_text_resume_file)
        parameters['outputFileDirectory'] = output_folder
        
        # Chạy bot
        create_and_run_bot(parameters, llm_api_key)
    except ConfigError as ce:
        logger.error(f"Lỗi cấu hình: {str(ce)}")
        logger.error(f"Tham khảo hướng dẫn cấu hình để khắc phục sự cố: https://github.com/feder-cr/AIHawk_AIHawk_automatic_job_application/blob/main/readme.md#configuration {str(ce)}")
    except FileNotFoundError as fnf:
        logger.error(f"Không tìm thấy file: {str(fnf)}")
        logger.error("Đảm bảo tất cả các file cần thiết có trong thư mục dữ liệu.")
        logger.error("Tham khảo hướng dẫn thiết lập file: https://github.com/feder-cr/AIHawk_AIHawk_automatic_job_application/blob/main/readme.md#configuration")
    except RuntimeError as re:
        logger.error(f"Lỗi thời gian chạy: {str(re)}")
        logger.error("Tham khảo hướng dẫn cấu hình và khắc phục sự cố: https://github.com/feder-cr/AIHawk_AIHawk_automatic_job_application/blob/main/readme.md#configuration")
    except Exception as e:
        logger.error(f"Đã xảy ra lỗi không mong muốn: {str(e)}")
        logger.error("Tham khảo hướng dẫn khắc phục sự cố chung: https://github.com/feder-cr/AIHawk_AIHawk_automatic_job_application/blob/main/readme.md#configuration")

if __name__ == "__main__":
    main()
