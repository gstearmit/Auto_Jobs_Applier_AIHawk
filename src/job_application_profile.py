# Import các thư viện cần thiết
from dataclasses import dataclass

import yaml

from loguru import logger

# Định nghĩa lớp dữ liệu cho thông tin tự nhận dạng
@dataclass
class SelfIdentification:
    gender: str
    pronouns: str
    veteran: str
    disability: str
    ethnicity: str

# Định nghĩa lớp dữ liệu cho thông tin ủy quyền pháp lý
@dataclass
class LegalAuthorization:
    eu_work_authorization: str
    us_work_authorization: str
    requires_us_visa: str
    legally_allowed_to_work_in_us: str
    requires_us_sponsorship: str
    requires_eu_visa: str
    legally_allowed_to_work_in_eu: str
    requires_eu_sponsorship: str
    canada_work_authorization: str
    requires_canada_visa: str
    legally_allowed_to_work_in_canada: str
    requires_canada_sponsorship: str
    uk_work_authorization: str
    requires_uk_visa: str 
    legally_allowed_to_work_in_uk: str
    requires_uk_sponsorship: str

# Định nghĩa lớp dữ liệu cho sở thích làm việc
@dataclass
class WorkPreferences:
    remote_work: str
    in_person_work: str
    open_to_relocation: str
    willing_to_complete_assessments: str
    willing_to_undergo_drug_tests: str
    willing_to_undergo_background_checks: str

# Định nghĩa lớp dữ liệu cho thông tin về tính khả dụng
@dataclass
class Availability:
    notice_period: str

# Định nghĩa lớp dữ liệu cho kỳ vọng về lương
@dataclass
class SalaryExpectations:
    salary_range_usd: str

# Định nghĩa lớp chính để quản lý hồ sơ ứng tuyển công việc
@dataclass
class JobApplicationProfile:
    self_identification: SelfIdentification
    legal_authorization: LegalAuthorization
    work_preferences: WorkPreferences
    availability: Availability
    salary_expectations: SalaryExpectations

    def __init__(self, yaml_str: str):
        logger.debug("Khởi tạo JobApplicationProfile với chuỗi YAML đã cung cấp")
        try:
            # Phân tích cú pháp chuỗi YAML
            data = yaml.safe_load(yaml_str)
            logger.debug(f"Dữ liệu YAML đã được phân tích thành công: {data}")
        except yaml.YAMLError as e:
            logger.error(f"Lỗi khi phân tích tệp YAML: {e}")
            raise ValueError("Lỗi khi phân tích tệp YAML.") from e
        except Exception as e:
            logger.error(f"Đã xảy ra lỗi không mong đợi khi phân tích tệp YAML: {e}")
            raise RuntimeError("Đã xảy ra lỗi không mong đợi khi phân tích tệp YAML.") from e

        if not isinstance(data, dict):
            logger.error(f"Dữ liệu YAML phải là một từ điển, nhận được: {type(data)}")
            raise TypeError("Dữ liệu YAML phải là một từ điển.")

        # Xử lý thông tin tự nhận dạng
        try:
            logger.debug("Đang xử lý thông tin tự nhận dạng")
            self.self_identification = SelfIdentification(**data['self_identification'])
            logger.debug(f"Thông tin tự nhận dạng đã được xử lý: {self.self_identification}")
        except KeyError as e:
            logger.error(f"Trường bắt buộc {e} bị thiếu trong dữ liệu tự nhận dạng.")
            raise KeyError(f"Trường bắt buộc {e} bị thiếu trong dữ liệu tự nhận dạng.") from e
        except TypeError as e:
            logger.error(f"Lỗi trong dữ liệu tự nhận dạng: {e}")
            raise TypeError(f"Lỗi trong dữ liệu tự nhận dạng: {e}") from e
        except AttributeError as e:
            logger.error(f"Lỗi thuộc tính trong quá trình xử lý thông tin tự nhận dạng: {e}")
            raise AttributeError("Lỗi thuộc tính trong quá trình xử lý thông tin tự nhận dạng.") from e
        except Exception as e:
            logger.error(f"Đã xảy ra lỗi không mong đợi khi xử lý thông tin tự nhận dạng: {e}")
            raise RuntimeError("Đã xảy ra lỗi không mong đợi khi xử lý thông tin tự nhận dạng.") from e

        # Xử lý thông tin ủy quyền pháp lý
        try:
            logger.debug("Đang xử lý thông tin ủy quyền pháp lý")
            self.legal_authorization = LegalAuthorization(**data['legal_authorization'])
            logger.debug(f"Thông tin ủy quyền pháp lý đã được xử lý: {self.legal_authorization}")
        except KeyError as e:
            logger.error(f"Trường bắt buộc {e} bị thiếu trong dữ liệu ủy quyền pháp lý.")
            raise KeyError(f"Trường bắt buộc {e} bị thiếu trong dữ liệu ủy quyền pháp lý.") from e
        except TypeError as e:
            logger.error(f"Lỗi trong dữ liệu ủy quyền pháp lý: {e}")
            raise TypeError(f"Lỗi trong dữ liệu ủy quyền pháp lý: {e}") from e
        except AttributeError as e:
            logger.error(f"Lỗi thuộc tính trong quá trình xử lý thông tin ủy quyền pháp lý: {e}")
            raise AttributeError("Lỗi thuộc tính trong quá trình xử lý thông tin ủy quyền pháp lý.") from e
        except Exception as e:
            logger.error(f"Đã xảy ra lỗi không mong đợi khi xử lý thông tin ủy quyền pháp lý: {e}")
            raise RuntimeError("Đã xảy ra lỗi không mong đợi khi xử lý thông tin ủy quyền pháp lý.") from e

        # Xử lý sở thích làm việc
        try:
            logger.debug("Đang xử lý sở thích làm việc")
            self.work_preferences = WorkPreferences(**data['work_preferences'])
            logger.debug(f"Sở thích làm việc đã được xử lý: {self.work_preferences}")
        except KeyError as e:
            logger.error(f"Trường bắt buộc {e} bị thiếu trong dữ liệu sở thích làm việc.")
            raise KeyError(f"Trường bắt buộc {e} bị thiếu trong dữ liệu sở thích làm việc.") from e
        except TypeError as e:
            logger.error(f"Lỗi trong dữ liệu sở thích làm việc: {e}")
            raise TypeError(f"Lỗi trong dữ liệu sở thích làm việc: {e}") from e
        except AttributeError as e:
            logger.error(f"Lỗi thuộc tính trong quá trình xử lý sở thích làm việc: {e}")
            raise AttributeError("Lỗi thuộc tính trong quá trình xử lý sở thích làm việc.") from e
        except Exception as e:
            logger.error(f"Đã xảy ra lỗi không mong đợi khi xử lý sở thích làm việc: {e}")
            raise RuntimeError("Đã xảy ra lỗi không mong đợi khi xử lý sở thích làm việc.") from e

        # Xử lý thông tin về tính khả dụng
        try:
            logger.debug("Đang xử lý thông tin về tính khả dụng")
            self.availability = Availability(**data['availability'])
            logger.debug(f"Thông tin về tính khả dụng đã được xử lý: {self.availability}")
        except KeyError as e:
            logger.error(f"Trường bắt buộc {e} bị thiếu trong dữ liệu về tính khả dụng.")
            raise KeyError(f"Trường bắt buộc {e} bị thiếu trong dữ liệu về tính khả dụng.") from e
        except TypeError as e:
            logger.error(f"Lỗi trong dữ liệu về tính khả dụng: {e}")
            raise TypeError(f"Lỗi trong dữ liệu về tính khả dụng: {e}") from e
        except AttributeError as e:
            logger.error(f"Lỗi thuộc tính trong quá trình xử lý thông tin về tính khả dụng: {e}")
            raise AttributeError("Lỗi thuộc tính trong quá trình xử lý thông tin về tính khả dụng.") from e
        except Exception as e:
            logger.error(f"Đã xảy ra lỗi không mong đợi khi xử lý thông tin về tính khả dụng: {e}")
            raise RuntimeError("Đã xảy ra lỗi không mong đợi khi xử lý thông tin về tính khả dụng.") from e

        # Xử lý kỳ vọng về lương
        try:
            logger.debug("Đang xử lý kỳ vọng về lương")
            self.salary_expectations = SalaryExpectations(**data['salary_expectations'])
            logger.debug(f"Kỳ vọng về lương đã được xử lý: {self.salary_expectations}")
        except KeyError as e:
            logger.error(f"Trường bắt buộc {e} bị thiếu trong dữ liệu kỳ vọng về lương.")
            raise KeyError(f"Trường bắt buộc {e} bị thiếu trong dữ liệu kỳ vọng về lương.") from e
        except TypeError as e:
            logger.error(f"Lỗi trong dữ liệu kỳ vọng về lương: {e}")
            raise TypeError(f"Lỗi trong dữ liệu kỳ vọng về lương: {e}") from e
        except AttributeError as e:
            logger.error(f"Lỗi thuộc tính trong quá trình xử lý kỳ vọng về lương: {e}")
            raise AttributeError("Lỗi thuộc tính trong quá trình xử lý kỳ vọng về lương.") from e
        except Exception as e:
            logger.error(f"Đã xảy ra lỗi không mong đợi khi xử lý kỳ vọng về lương: {e}")
            raise RuntimeError("Đã xảy ra lỗi không mong đợi khi xử lý kỳ vọng về lương.") from e

        logger.debug("Khởi tạo JobApplicationProfile đã hoàn thành thành công.")

    def __str__(self):
        logger.debug("Đang tạo biểu diễn chuỗi của JobApplicationProfile")

        def format_dataclass(obj):
            return "\n".join(f"{field.name}: {getattr(obj, field.name)}" for field in obj.__dataclass_fields__.values())

        formatted_str = (f"Thông tin tự nhận dạng:\n{format_dataclass(self.self_identification)}\n\n"
                         f"Ủy quyền pháp lý:\n{format_dataclass(self.legal_authorization)}\n\n"
                         f"Sở thích làm việc:\n{format_dataclass(self.work_preferences)}\n\n"
                         f"Tính khả dụng: {self.availability.notice_period}\n\n"
                         f"Kỳ vọng về lương: {self.salary_expectations.salary_range_usd}\n\n")
        logger.debug(f"Biểu diễn chuỗi đã được tạo: {formatted_str}")
        return formatted_str
