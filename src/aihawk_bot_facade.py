from loguru import logger


class AIHawkBotState:
    def __init__(self):
        logger.debug("Khởi tạo AIHawkBotState")
        self.reset()

    def reset(self):
        logger.debug("Đặt lại AIHawkBotState")
        # Đặt lại tất cả các trạng thái về false
        self.credentials_set = False
        self.api_key_set = False
        self.job_application_profile_set = False
        self.gpt_answerer_set = False
        self.parameters_set = False
        self.logged_in = False

    def validate_state(self, required_keys):
        logger.debug(f"Xác thực AIHawkBotState với các khóa bắt buộc: {required_keys}")
        # Kiểm tra xem tất cả các khóa bắt buộc đã được thiết lập chưa
        for key in required_keys:
            if not getattr(self, key):
                logger.error(f"Xác thực trạng thái thất bại: {key} chưa được thiết lập")
                raise ValueError(f"{key.replace('_', ' ').capitalize()} phải được thiết lập trước khi tiếp tục.")
        logger.debug("Xác thực trạng thái thành công")


class AIHawkBotFacade:
    def __init__(self, login_component, apply_component):
        logger.debug("Khởi tạo AIHawkBotFacade")
        self.login_component = login_component
        self.apply_component = apply_component
        self.state = AIHawkBotState()
        self.job_application_profile = None
        self.resume = None
        self.email = None
        self.password = None
        self.parameters = None

    def set_job_application_profile_and_resume(self, job_application_profile, resume):
        logger.debug("Thiết lập hồ sơ ứng tuyển và sơ yếu lý lịch")
        # Kiểm tra tính hợp lệ của dữ liệu đầu vào
        self._validate_non_empty(job_application_profile, "Hồ sơ ứng tuyển")
        self._validate_non_empty(resume, "Sơ yếu lý lịch")
        self.job_application_profile = job_application_profile
        self.resume = resume
        self.state.job_application_profile_set = True
        logger.debug("Hồ sơ ứng tuyển và sơ yếu lý lịch đã được thiết lập thành công")


    def set_gpt_answerer_and_resume_generator(self, gpt_answerer_component, resume_generator_manager):
        logger.debug("Thiết lập GPT answerer và trình tạo sơ yếu lý lịch")
        # Đảm bảo hồ sơ và sơ yếu lý lịch đã được thiết lập
        self._ensure_job_profile_and_resume_set()
        gpt_answerer_component.set_job_application_profile(self.job_application_profile)
        gpt_answerer_component.set_resume(self.resume)
        self.apply_component.set_gpt_answerer(gpt_answerer_component)
        self.apply_component.set_resume_generator_manager(resume_generator_manager)
        self.state.gpt_answerer_set = True
        logger.debug("GPT answerer và trình tạo sơ yếu lý lịch đã được thiết lập thành công")

    def set_parameters(self, parameters):
        logger.debug("Thiết lập các tham số")
        # Kiểm tra tính hợp lệ của tham số
        self._validate_non_empty(parameters, "Các tham số")
        self.parameters = parameters
        self.apply_component.set_parameters(parameters)
        self.state.credentials_set = True
        self.state.parameters_set = True
        logger.debug("Các tham số đã được thiết lập thành công")

    def start_login(self):
        logger.debug("Bắt đầu quá trình đăng nhập")
        # Kiểm tra xem thông tin đăng nhập đã được thiết lập chưa
        self.state.validate_state(['credentials_set'])
        self.login_component.start()
        self.state.logged_in = True
        logger.debug("Quá trình đăng nhập đã hoàn tất thành công")

    def start_apply(self):
        logger.debug("Bắt đầu quá trình ứng tuyển")
        # Kiểm tra xem tất cả các điều kiện cần thiết đã được đáp ứng chưa
        self.state.validate_state(['logged_in', 'job_application_profile_set', 'gpt_answerer_set', 'parameters_set'])
        self.apply_component.start_applying()
        logger.debug("Quá trình ứng tuyển đã bắt đầu thành công")

    def _validate_non_empty(self, value, name):
        logger.debug(f"Kiểm tra {name} không được để trống")
        if not value:
            logger.error(f"Kiểm tra thất bại: {name} đang trống")
            raise ValueError(f"{name} không thể để trống.")
        logger.debug(f"Kiểm tra thành công cho {name}")

    def _ensure_job_profile_and_resume_set(self):
        logger.debug("Đảm bảo hồ sơ công việc và sơ yếu lý lịch đã được thiết lập")
        if not self.state.job_application_profile_set:
            logger.error("Hồ sơ ứng tuyển và sơ yếu lý lịch chưa được thiết lập")
            raise ValueError("Hồ sơ ứng tuyển và sơ yếu lý lịch phải được thiết lập trước khi tiếp tục.")
        logger.debug("Hồ sơ công việc và sơ yếu lý lịch đã được thiết lập")
