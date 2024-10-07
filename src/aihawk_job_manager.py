# Import các thư viện cần thiết
import json
import os
import random
import time
from itertools import product
from pathlib import Path

from inputimeout import inputimeout, TimeoutOccurred
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import src.utils as utils
from app_config import MINIMUM_WAIT_TIME
from src.job import Job
from src.aihawk_easy_applier import AIHawkEasyApplier
from loguru import logger

# Lớp để quản lý các khóa môi trường
class EnvironmentKeys:
    def __init__(self):
        logger.debug("Khởi tạo EnvironmentKeys")
        self.skip_apply = self._read_env_key_bool("SKIP_APPLY")
        self.disable_description_filter = self._read_env_key_bool("DISABLE_DESCRIPTION_FILTER")
        logger.debug(f"EnvironmentKeys đã khởi tạo: skip_apply={self.skip_apply}, disable_description_filter={self.disable_description_filter}")

    # Phương thức tĩnh để đọc giá trị khóa môi trường
    @staticmethod
    def _read_env_key(key: str) -> str:
        value = os.getenv(key, "")
        logger.debug(f"Đọc khóa môi trường {key}: {value}")
        return value

    # Phương thức tĩnh để đọc giá trị khóa môi trường dưới dạng boolean
    @staticmethod
    def _read_env_key_bool(key: str) -> bool:
        value = os.getenv(key) == "True"
        logger.debug(f"Đọc khóa môi trường {key} dưới dạng boolean: {value}")
        return value

# Lớp chính để quản lý việc tìm kiếm và ứng tuyển công việc
class AIHawkJobManager:
    def __init__(self, driver):
        logger.debug("Khởi tạo AIHawkJobManager")
        self.driver = driver
        self.set_old_answers = set()
        self.easy_applier_component = None
        logger.debug("AIHawkJobManager đã khởi tạo thành công")

    # Thiết lập các tham số cho quá trình tìm kiếm và ứng tuyển
    def set_parameters(self, parameters):
        logger.debug("Thiết lập tham số cho AIHawkJobManager")
        self.company_blacklist = parameters.get('company_blacklist', []) or []
        self.title_blacklist = parameters.get('title_blacklist', []) or []
        self.positions = parameters.get('positions', [])
        self.locations = parameters.get('locations', [])
        self.apply_once_at_company = parameters.get('apply_once_at_company', False)
        self.base_search_url = self.get_base_search_url(parameters)
        self.seen_jobs = []

        job_applicants_threshold = parameters.get('job_applicants_threshold', {})
        self.min_applicants = job_applicants_threshold.get('min_applicants', 0)
        self.max_applicants = job_applicants_threshold.get('max_applicants', float('inf'))

        resume_path = parameters.get('uploads', {}).get('resume', None)
        self.resume_path = Path(resume_path) if resume_path and Path(resume_path).exists() else None
        self.output_file_directory = Path(parameters['outputFileDirectory'])
        self.env_config = EnvironmentKeys()
        logger.debug("Các tham số đã được thiết lập thành công")

    # Thiết lập bộ trả lời GPT
    def set_gpt_answerer(self, gpt_answerer):
        logger.debug("Thiết lập bộ trả lời GPT")
        self.gpt_answerer = gpt_answerer

    # Thiết lập trình quản lý tạo CV
    def set_resume_generator_manager(self, resume_generator_manager):
        logger.debug("Thiết lập trình quản lý tạo CV")
        self.resume_generator_manager = resume_generator_manager

    # Bắt đầu quá trình ứng tuyển
    def start_applying(self):
        logger.debug("Bắt đầu quá trình ứng tuyển công việc")
        self.easy_applier_component = AIHawkEasyApplier(self.driver, self.resume_path, self.set_old_answers,
                                                          self.gpt_answerer, self.resume_generator_manager)
        searches = list(product(self.positions, self.locations))
        random.shuffle(searches)
        page_sleep = 0
        minimum_time = MINIMUM_WAIT_TIME
        minimum_page_time = time.time() + minimum_time

        for position, location in searches:
            location_url = "&location=" + location
            job_page_number = -1
            logger.debug(f"Bắt đầu tìm kiếm cho vị trí {position} tại {location}.")

            try:
                while True:
                    page_sleep += 1
                    job_page_number += 1
                    logger.debug(f"Chuyển đến trang công việc {job_page_number}")
                    self.next_job_page(position, location_url, job_page_number)
                    time.sleep(random.uniform(1.5, 3.5))
                    logger.debug("Bắt đầu quá trình ứng tuyển cho trang này...")

                    try:
                        jobs = self.get_jobs_from_page()
                        if not jobs:
                            logger.debug("Không còn công việc nào trên trang này. Thoát vòng lặp.")
                            break
                    except Exception as e:
                        logger.error(f"Không thể lấy danh sách công việc: {e}")
                        break

                    try:
                        self.apply_jobs()
                    except Exception as e:
                        logger.error(f"Lỗi trong quá trình ứng tuyển: {e}")
                        continue

                    logger.debug("Đã hoàn thành việc ứng tuyển các công việc trên trang này!")

                    time_left = minimum_page_time - time.time()

                    # Hỏi người dùng có muốn bỏ qua thời gian chờ không, với thời gian chờ
                    if time_left > 0:
                        try:
                            user_input = inputimeout(
                                prompt=f"Đang chờ {time_left} giây. Nhấn 'y' để bỏ qua thời gian chờ. Hết thời gian sau 60 giây : ",
                                timeout=60).strip().lower()
                        except TimeoutOccurred:
                            user_input = ''  # Không có đầu vào sau khi hết thời gian
                        if user_input == 'y':
                            logger.debug("Người dùng chọn bỏ qua thời gian chờ.")
                        else:
                            logger.debug(f"Đang chờ {time_left} giây vì người dùng không chọn bỏ qua.")
                            time.sleep(time_left)

                    minimum_page_time = time.time() + minimum_time

                    if page_sleep % 5 == 0:
                        sleep_time = random.randint(5, 34)
                        try:
                            user_input = inputimeout(
                                prompt=f"Đang chờ {sleep_time / 60} phút. Nhấn 'y' để bỏ qua thời gian chờ. Hết thời gian sau 60 giây : ",
                                timeout=60).strip().lower()
                        except TimeoutOccurred:
                            user_input = ''  # Không có đầu vào sau khi hết thời gian
                        if user_input == 'y':
                            logger.debug("Người dùng chọn bỏ qua thời gian chờ.")
                        else:
                            logger.debug(f"Đang chờ {sleep_time} giây.")
                            time.sleep(sleep_time)
                        page_sleep += 1
            except Exception as e:
                logger.error(f"Lỗi không mong đợi trong quá trình tìm kiếm công việc: {e}")
                continue

            time_left = minimum_page_time - time.time()

            if time_left > 0:
                try:
                    user_input = inputimeout(
                        prompt=f"Đang chờ {time_left} giây. Nhấn 'y' để bỏ qua thời gian chờ. Hết thời gian sau 60 giây : ",
                        timeout=60).strip().lower()
                except TimeoutOccurred:
                    user_input = ''  # Không có đầu vào sau khi hết thời gian
                if user_input == 'y':
                    logger.debug("Người dùng chọn bỏ qua thời gian chờ.")
                else:
                    logger.debug(f"Đang chờ {time_left} giây vì người dùng không chọn bỏ qua.")
                    time.sleep(time_left)

            minimum_page_time = time.time() + minimum_time

            if page_sleep % 5 == 0:
                sleep_time = random.randint(50, 90)
                try:
                    user_input = inputimeout(
                        prompt=f"Đang chờ {sleep_time / 60} phút. Nhấn 'y' để bỏ qua thời gian chờ: ",
                        timeout=60).strip().lower()
                except TimeoutOccurred:
                    user_input = ''  # Không có đầu vào sau khi hết thời gian
                if user_input == 'y':
                    logger.debug("Người dùng chọn bỏ qua thời gian chờ.")
                else:
                    logger.debug(f"Đang chờ {sleep_time} giây.")
                    time.sleep(sleep_time)
                page_sleep += 1

    # Lấy danh sách công việc từ trang hiện tại
    def get_jobs_from_page(self):

        try:

            no_jobs_element = self.driver.find_element(By.CLASS_NAME, 'jobs-search-two-pane__no-results-banner--expand')
            if 'No matching jobs found' in no_jobs_element.text or 'unfortunately, things aren' in self.driver.page_source.lower():
                logger.debug("Không tìm thấy công việc phù hợp trên trang này, bỏ qua.")
                return []

        except NoSuchElementException:
            pass

        try:
            job_results = self.driver.find_element(By.CLASS_NAME, "jobs-search-results-list")
            utils.scroll_slow(self.driver, job_results)
            utils.scroll_slow(self.driver, job_results, step=300, reverse=True)

            job_list_elements = self.driver.find_elements(By.CLASS_NAME, 'scaffold-layout__list-container')[
                0].find_elements(By.CLASS_NAME, 'jobs-search-results__list-item')
            if not job_list_elements:
                logger.debug("Không tìm thấy phần tử công việc nào trên trang, bỏ qua.")
                return []

            return job_list_elements

        except NoSuchElementException:
            logger.debug("Không tìm thấy kết quả công việc nào trên trang.")
            return []

        except Exception as e:
            logger.error(f"Lỗi khi lấy các phần tử công việc: {e}")
            return []

    # Ứng tuyển các công việc
    def apply_jobs(self):
        try:
            no_jobs_element = self.driver.find_element(By.CLASS_NAME, 'jobs-search-two-pane__no-results-banner--expand')
            if 'No matching jobs found' in no_jobs_element.text or 'unfortunately, things aren' in self.driver.page_source.lower():
                logger.debug("Không tìm thấy công việc phù hợp trên trang này, bỏ qua")
                return
        except NoSuchElementException:
            pass

        job_list_elements = self.driver.find_elements(By.CLASS_NAME, 'scaffold-layout__list-container')[
            0].find_elements(By.CLASS_NAME, 'jobs-search-results__list-item')

        if not job_list_elements:
            logger.debug("Không tìm thấy phần tử công việc nào trên trang, bỏ qua")
            return

        job_list = [Job(*self.extract_job_information_from_tile(job_element)) for job_element in job_list_elements]

        for job in job_list:

            logger.debug(f"Bắt đầu ứng tuyển cho công việc: {job.title} tại {job.company}")
            #TODO fix apply threshold
            """
                # Initialize applicants_count as None
                applicants_count = None

                # Iterate over each job insight element to find the one containing the word "applicant"
                for element in job_insight_elements:
                    logger.debug(f"Checking element text: {element.text}")
                    if "applicant" in element.text.lower():
                        # Found an element containing "applicant"
                        applicants_text = element.text.strip()
                        logger.debug(f"Applicants text found: {applicants_text}")

                        # Extract numeric digits from the text (e.g., "70 applicants" -> "70")
                        applicants_count = ''.join(filter(str.isdigit, applicants_text))
                        logger.debug(f"Extracted applicants count: {applicants_count}")

                        if applicants_count:
                            if "over" in applicants_text.lower():
                                applicants_count = int(applicants_count) + 1  # Handle "over X applicants"
                                logger.debug(f"Applicants count adjusted for 'over': {applicants_count}")
                            else:
                                applicants_count = int(applicants_count)  # Convert the extracted number to an integer
                        break

                # Check if applicants_count is valid (not None) before performing comparisons
                if applicants_count is not None:
                    # Perform the threshold check for applicants count
                    if applicants_count < self.min_applicants or applicants_count > self.max_applicants:
                        logger.debug(f"Skipping {job.title} at {job.company}, applicants count: {applicants_count}")
                        self.write_to_file(job, "skipped_due_to_applicants")
                        continue  # Skip this job if applicants count is outside the threshold
                    else:
                        logger.debug(f"Applicants count {applicants_count} is within the threshold")
                else:
                    # If no applicants count was found, log a warning but continue the process
                    logger.warning(
                        f"Applicants count not found for {job.title} at {job.company}, continuing with application.")
            except NoSuchElementException:
                # Log a warning if the job insight elements are not found, but do not stop the job application process
                logger.warning(
                    f"Applicants count elements not found for {job.title} at {job.company}, continuing with application.")
            except ValueError as e:
                # Handle errors when parsing the applicants count
                logger.error(f"Error parsing applicants count for {job.title} at {job.company}: {e}")
            except Exception as e:
                # Catch any other exceptions to ensure the process continues
                logger.error(
                    f"Unexpected error during applicants count processing for {job.title} at {job.company}: {e}")

            # Continue with the job application process regardless of the applicants count check
            """
        

            if self.is_blacklisted(job.title, job.company, job.link):
                logger.debug(f"Công việc trong danh sách đen: {job.title} tại {job.company}")
                self.write_to_file(job, "skipped")
                continue
            if self.is_already_applied_to_job(job.title, job.company, job.link):
                self.write_to_file(job, "skipped")
                continue
            if self.is_already_applied_to_company(job.company):
                self.write_to_file(job, "skipped")
                continue
            try:
                if job.apply_method not in {"Continue", "Applied", "Apply"}:
                    self.easy_applier_component.job_apply(job)
                    self.write_to_file(job, "success")
                    logger.debug(f"Đã ứng tuyển công việc: {job.title} tại {job.company}")
            except Exception as e:
                logger.error(f"Không thể ứng tuyển cho {job.title} tại {job.company}: {e}")
                self.write_to_file(job, "failed")
                continue

    # Ghi thông tin công việc vào file
    def write_to_file(self, job, file_name):
        logger.debug(f"Đang ghi kết quả ứng tuyển công việc vào file: {file_name}")
        pdf_path = Path(job.pdf_path).resolve()
        pdf_path = pdf_path.as_uri()
        data = {
            "company": job.company,
            "job_title": job.title,
            "link": job.link,
            "job_recruiter": job.recruiter_link,
            "job_location": job.location,
            "pdf_path": pdf_path
        }
        file_path = self.output_file_directory / f"{file_name}.json"
        if not file_path.exists():
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([data], f, indent=4)
                logger.debug(f"Dữ liệu công việc đã được ghi vào file mới: {file_name}")
        else:
            with open(file_path, 'r+', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    logger.error(f"Lỗi giải mã JSON trong file: {file_path}")
                    existing_data = []
                existing_data.append(data)
                f.seek(0)
                json.dump(existing_data, f, indent=4)
                f.truncate()
                logger.debug(f"Dữ liệu công việc đã được thêm vào file hiện có: {file_name}")

    # Tạo URL cơ bản cho tìm kiếm công việc
    def get_base_search_url(self, parameters):
        logger.debug("Đang tạo URL cơ bản cho tìm kiếm")
        url_parts = []
        if parameters['remote']:
            url_parts.append("f_CF=f_WRA")
        experience_levels = [str(i + 1) for i, (level, v) in enumerate(parameters.get('experience_level', {}).items()) if
                             v]
        if experience_levels:
            url_parts.append(f"f_E={','.join(experience_levels)}")
        url_parts.append(f"distance={parameters['distance']}")
        job_types = [key[0].upper() for key, value in parameters.get('jobTypes', {}).items() if value]
        if job_types:
            url_parts.append(f"f_JT={','.join(job_types)}")
        date_mapping = {
            "all time": "",
            "month": "&f_TPR=r2592000",
            "week": "&f_TPR=r604800",
            "24 hours": "&f_TPR=r86400"
        }
        date_param = next((v for k, v in date_mapping.items() if parameters.get('date', {}).get(k)), "")
        url_parts.append("f_LF=f_AL")  # Easy Apply
        base_url = "&".join(url_parts)
        full_url = f"?{base_url}{date_param}"
        logger.debug(f"URL cơ bản đã được tạo: {full_url}")
        return full_url

    # Chuyển đến trang công việc tiếp theo
    def next_job_page(self, position, location, job_page):
        logger.debug(f"Đang chuyển đến trang công việc tiếp theo: {position} tại {location}, trang {job_page}")
        self.driver.get(
            f"https://www.linkedin.com/jobs/search/{self.base_search_url}&keywords={position}{location}&start={job_page * 25}")

    # Trích xuất thông tin công việc từ phần tử trên trang
    def extract_job_information_from_tile(self, job_tile):
        logger.debug("Đang trích xuất thông tin công việc từ phần tử")
        job_title, company, job_location, apply_method, link = "", "", "", "", ""
        try:
            print(job_tile.get_attribute('outerHTML'))
            job_title = job_tile.find_element(By.CLASS_NAME, 'job-card-list__title').find_element(By.TAG_NAME, 'strong').text
            
            link = job_tile.find_element(By.CLASS_NAME, 'job-card-list__title').get_attribute('href').split('?')[0]
            company = job_tile.find_element(By.CLASS_NAME, 'job-card-container__primary-description').text
            logger.debug(f"Thông tin công việc đã được trích xuất: {job_title} tại {company}")
        except NoSuchElementException:
            logger.warning("Một số thông tin công việc (tiêu đề, liên kết hoặc công ty) bị thiếu.")
        try:
            job_location = job_tile.find_element(By.CLASS_NAME, 'job-card-container__metadata-item').text
        except NoSuchElementException:
            logger.warning("Địa điểm công việc bị thiếu.")
        try:
            apply_method = job_tile.find_element(By.CLASS_NAME, 'job-card-container__apply-method').text
        except NoSuchElementException:
            apply_method = "Applied"
            logger.warning("Không tìm thấy phương thức ứng tuyển, giả định là 'Applied'.")

        return job_title, company, job_location, link, apply_method

    # Kiểm tra xem công việc có trong danh sách đen không
    def is_blacklisted(self, job_title, company, link):
        logger.debug(f"Đang kiểm tra xem công việc có trong danh sách đen không: {job_title} tại {company}")
        job_title_words = job_title.lower().split(' ')
        title_blacklisted = any(word in job_title_words for word in self.title_blacklist)
        company_blacklisted = company.strip().lower() in (word.strip().lower() for word in self.company_blacklist)
        link_seen = link in self.seen_jobs
        is_blacklisted = title_blacklisted or company_blacklisted or link_seen
        logger.debug(f"Trạng thái trong danh sách đen của công việc: {is_blacklisted}")

        return title_blacklisted or company_blacklisted or link_seen

    # Kiểm tra xem đã ứng tuyển công việc này chưa
    def is_already_applied_to_job(self, job_title, company, link):
        link_seen = link in self.seen_jobs
        if link_seen:
            logger.debug(f"Đã ứng tuyển công việc: {job_title} tại {company}, bỏ qua...")
        return link_seen

    # Kiểm tra xem đã ứng tuyển tại công ty này chưa
    def is_already_applied_to_company(self, company):
        if not self.apply_once_at_company:
            return False

        output_files = ["success.json"]
        for file_name in output_files:
            file_path = self.output_file_directory / file_name
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        existing_data = json.load(f)
                        for applied_job in existing_data:
                            if applied_job['company'].strip().lower() == company.strip().lower():
                                logger.debug(
                                    f"Đã ứng tuyển tại {company} (chính sách một lần mỗi công ty), bỏ qua...")
                                return True
                    except json.JSONDecodeError:
                        continue
        return False
