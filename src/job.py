# Import các thư viện cần thiết
from dataclasses import dataclass

from loguru import logger


# Định nghĩa lớp Job sử dụng dataclass để tự động tạo các phương thức __init__, __repr__, __eq__, v.v.
@dataclass
class Job:
    title: str  # Tiêu đề công việc
    company: str  # Tên công ty
    location: str  # Địa điểm làm việc
    link: str  # Liên kết đến thông tin công việc
    apply_method: str  # Phương thức ứng tuyển
    description: str = ""  # Mô tả công việc (mặc định là chuỗi rỗng)
    summarize_job_description: str = ""  # Tóm tắt mô tả công việc (mặc định là chuỗi rỗng)
    pdf_path: str = ""  # Đường dẫn đến file PDF (nếu có)
    recruiter_link: str = ""  # Liên kết đến hồ sơ người tuyển dụng (nếu có)

    def set_summarize_job_description(self, summarize_job_description):
        # Phương thức để cập nhật tóm tắt mô tả công việc
        logger.debug(f"Đang cập nhật tóm tắt mô tả công việc: {summarize_job_description}")
        self.summarize_job_description = summarize_job_description

    def set_job_description(self, description):
        # Phương thức để cập nhật mô tả công việc đầy đủ
        logger.debug(f"Đang cập nhật mô tả công việc: {description}")
        self.description = description

    def set_recruiter_link(self, recruiter_link):
        # Phương thức để cập nhật liên kết đến hồ sơ người tuyển dụng
        logger.debug(f"Đang cập nhật liên kết người tuyển dụng: {recruiter_link}")
        self.recruiter_link = recruiter_link

    def formatted_job_information(self):
        """
        Định dạng thông tin công việc dưới dạng chuỗi markdown.
        """
        logger.debug(f"Đang định dạng thông tin công việc cho: {self.title} tại {self.company}")
        job_information = f"""
        # Mô tả công việc
        ## Thông tin công việc 
        - Vị trí: {self.title}
        - Tại: {self.company}
        - Địa điểm: {self.location}
        - Hồ sơ người tuyển dụng: {self.recruiter_link or 'Không có sẵn'}
        
        ## Mô tả
        {self.description or 'Không có mô tả được cung cấp.'}
        """
        formatted_information = job_information.strip()
        logger.debug(f"Thông tin công việc đã được định dạng: {formatted_information}")
        return formatted_information
