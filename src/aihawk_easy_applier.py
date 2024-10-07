import base64
import json
import os
import random
import re
import time
import traceback
from typing import List, Optional, Any, Tuple

from httpx import HTTPStatusError
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

import src.utils as utils
from loguru import logger


class AIHawkEasyApplier:
    def __init__(self, driver: Any, resume_dir: Optional[str], set_old_answers: List[Tuple[str, str, str]],
                 gpt_answerer: Any, resume_generator_manager):
        # Khởi tạo AIHawkEasyApplier với các tham số cần thiết
        logger.debug("Khởi tạo AIHawkEasyApplier")
        if resume_dir is None or not os.path.exists(resume_dir):
            resume_dir = None
        self.driver = driver
        self.resume_path = resume_dir
        self.set_old_answers = set_old_answers
        self.gpt_answerer = gpt_answerer
        self.resume_generator_manager = resume_generator_manager
        self.all_data = self._load_questions_from_json()

        logger.debug("AIHawkEasyApplier đã được khởi tạo thành công")

    def _load_questions_from_json(self) -> List[dict]:
        # Tải dữ liệu câu hỏi từ file JSON
        output_file = 'answers.json'
        logger.debug(f"Đang tải câu hỏi từ file JSON: {output_file}")
        try:
            with open(output_file, 'r') as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, list):
                        raise ValueError("Định dạng file JSON không chính xác. Cần một danh sách các câu hỏi.")
                except json.JSONDecodeError:
                    logger.error("Giải mã JSON thất bại")
                    data = []
            logger.debug("Câu hỏi đã được tải thành công từ JSON")
            return data
        except FileNotFoundError:
            logger.warning("Không tìm thấy file JSON, trả về danh sách trống")
            return []
        except Exception:
            tb_str = traceback.format_exc()
            logger.error(f"Lỗi khi tải dữ liệu câu hỏi từ file JSON: {tb_str}")
            raise Exception(f"Lỗi khi tải dữ liệu câu hỏi từ file JSON: \nTraceback:\n{tb_str}")

    def check_for_premium_redirect(self, job: Any, max_attempts=3):
        # Kiểm tra và xử lý chuyển hướng đến trang Premium

        current_url = self.driver.current_url
        attempts = 0

        while "linkedin.com/premium" in current_url and attempts < max_attempts:
            logger.warning("Đã chuyển hướng đến trang AIHawk Premium. Đang cố gắng quay lại trang công việc.")
            attempts += 1

            self.driver.get(job.link)
            time.sleep(2)
            current_url = self.driver.current_url

        if "linkedin.com/premium" in current_url:
            logger.error(f"Không thể quay lại trang công việc sau {max_attempts} lần thử. Không thể ứng tuyển công việc.")
            raise Exception(
                f"Đã chuyển hướng đến trang AIHawk Premium và không thể quay lại sau {max_attempts} lần thử. Hủy ứng tuyển công việc.")
            
    def apply_to_job(self, job: Any) -> None:
        """
        Bắt đầu quá trình ứng tuyển công việc.
        :param job: Đối tượng công việc chứa thông tin chi tiết.
        :return: None
        """
        logger.debug(f"Đang ứng tuyển công việc: {job}")
        try:
            self.job_apply(job)
            logger.info(f"Đã ứng tuyển thành công công việc: {job.title}")
        except Exception as e:
            logger.error(f"Không thể ứng tuyển công việc: {job.title}, lỗi: {str(e)}")
            raise e

    def job_apply(self, job: Any):
        logger.debug(f"Bắt đầu quá trình ứng tuyển cho công việc: {job}")

        try:
            self.driver.get(job.link)
            logger.debug(f"Đã điều hướng đến liên kết công việc: {job.link}")
        except Exception as e:
            logger.error(f"Không thể điều hướng đến liên kết công việc: {job.link}, lỗi: {str(e)}")
            raise

        time.sleep(random.uniform(3, 5))
        self.check_for_premium_redirect(job)

        try:
            # Xóa focus khỏi phần tử đang active
            self.driver.execute_script("document.activeElement.blur();")
            logger.debug("Đã xóa focus khỏi phần tử đang active")

            self.check_for_premium_redirect(job)

            easy_apply_button = self._find_easy_apply_button(job)

            self.check_for_premium_redirect(job)

            logger.debug("Đang lấy mô tả công việc")
            job_description = self._get_job_description()
            job.set_job_description(job_description)
            logger.debug(f"Đã thiết lập mô tả công việc: {job_description[:100]}")

            logger.debug("Đang lấy liên kết người tuyển dụng")
            recruiter_link = self._get_job_recruiter()
            job.set_recruiter_link(recruiter_link)
            logger.debug(f"Đã thiết lập liên kết người tuyển dụng: {recruiter_link}")

            logger.debug("Đang cố gắng nhấp vào nút 'Ứng tuyển ngay'")
            actions = ActionChains(self.driver)
            actions.move_to_element(easy_apply_button).click().perform()
            logger.debug("Đã nhấp thành công vào nút 'Ứng tuyển ngay'")

            logger.debug("Đang chuyển thông tin công việc cho GPT Answerer")
            self.gpt_answerer.set_job(job)

            logger.debug("Đang điền form ứng tuyển")
            self._fill_application_form(job)
            logger.debug(f"Quá trình ứng tuyển công việc đã hoàn tất thành công cho công việc: {job}")

        except Exception as e:
            # Xử lý lỗi và ghi log
            tb_str = traceback.format_exc()
            logger.error(f"Không thể ứng tuyển công việc: {job}, lỗi: {tb_str}")

            logger.debug("Đang hủy ứng tuyển do lỗi")
            self._discard_application()

            raise Exception(f"Không thể ứng tuyển công việc! Lỗi gốc:\nTraceback:\n{tb_str}")

    def _find_easy_apply_button(self, job: Any) -> WebElement:
        logger.debug("Đang tìm kiếm nút 'Ứng tuyển ngay'")
        attempt = 0

        search_methods = [
            {
                'description': "tìm tất cả các nút 'Ứng tuyển ngay' bằng find_elements",
                'find_elements': True,
                'xpath': '//button[contains(@class, "jobs-apply-button") and contains(., "Easy Apply")]'
            },
            {
                'description': "'aria-label' chứa 'Easy Apply to'",
                'xpath': '//button[contains(@aria-label, "Easy Apply to")]'
            },
            {
                'description': "tìm kiếm văn bản nút",
                'xpath': '//button[contains(text(), "Easy Apply") or contains(text(), "Apply now")]'
            }
        ]

        while attempt < 2:
            # Kiểm tra chuyển hướng và cuộn trang
            self.check_for_premium_redirect(job)
            self._scroll_page()

            for method in search_methods:
                try:
                    logger.debug(f"Đang thử tìm kiếm bằng {method['description']}")

                    if method.get('find_elements'):
                        # Tìm tất cả các nút phù hợp
                        buttons = self.driver.find_elements(By.XPATH, method['xpath'])
                        if buttons:
                            for index, button in enumerate(buttons):
                                try:
                                    # Đợi cho đến khi nút hiển thị và có thể nhấp được
                                    WebDriverWait(self.driver, 10).until(EC.visibility_of(button))
                                    WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(button))
                                    logger.debug(f"Đã tìm thấy nút 'Ứng tuyển ngay' {index + 1}, đang cố gắng nhấp")
                                    return button
                                except Exception as e:
                                    logger.warning(f"Nút {index + 1} được tìm thấy nhưng không thể nhấp: {e}")
                        else:
                            raise TimeoutException("Không tìm thấy nút 'Ứng tuyển ngay'")
                    else:
                        # Tìm một nút duy nhất
                        button = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, method['xpath']))
                        )
                        WebDriverWait(self.driver, 10).until(EC.visibility_of(button))
                        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(button))
                        logger.debug("Đã tìm thấy nút 'Ứng tuyển ngay', đang cố gắng nhấp")
                        return button

                except TimeoutException:
                    logger.warning(f"Hết thời gian chờ khi tìm kiếm bằng {method['description']}")
                except Exception as e:
                    logger.warning(
                        f"Không thể nhấp vào nút 'Ứng tuyển ngay' bằng {method['description']} ở lần thử {attempt + 1}: {e}")

            self.check_for_premium_redirect(job)

            if attempt == 0:
                logger.debug("Đang làm mới trang để thử tìm lại nút 'Ứng tuyển ngay'")
                self.driver.refresh()
                time.sleep(random.randint(3, 5))
            attempt += 1

        page_source = self.driver.page_source
        logger.error(f"Không tìm thấy nút 'Ứng tuyển ngay' có thể nhấp được sau 2 lần thử. Nguồn trang:\n{page_source}")
        raise Exception("Không tìm thấy nút 'Ứng tuyển ngay' có thể nhấp được")

    def _get_job_description(self) -> str:
        logger.debug("Đang lấy mô tả công việc")
        try:
            try:
                see_more_button = self.driver.find_element(By.XPATH,
                                                           '//button[@aria-label="Click to see more description"]')
                actions = ActionChains(self.driver)
                actions.move_to_element(see_more_button).click().perform()
                time.sleep(2)
            except NoSuchElementException:
                logger.debug("Không tìm thấy nút 'Xem thêm', bỏ qua")

            description = self.driver.find_element(By.CLASS_NAME, 'jobs-description-content__text').text
            logger.debug("Đã lấy mô tả công việc thành công")
            return description
        except NoSuchElementException:
            tb_str = traceback.format_exc()
            logger.error(f"Không tìm thấy mô tả công việc: {tb_str}")
            raise Exception(f"Không tìm thấy mô tả công việc: \nTraceback:\n{tb_str}")
        except Exception:
            tb_str = traceback.format_exc()
            logger.error(f"Lỗi khi lấy mô tả công việc: {tb_str}")
            raise Exception(f"Lỗi khi lấy mô tả công việc: \nTraceback:\n{tb_str}")

    def _get_job_recruiter(self):
        logger.debug("Đang lấy thông tin người tuyển dụng")
        try:
            hiring_team_section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//h2[text()="Meet the hiring team"]'))
            )
            logger.debug("Đã tìm thấy phần thông tin đội ngũ tuyển dụng")

            recruiter_elements = hiring_team_section.find_elements(By.XPATH,
                                                                   './/following::a[contains(@href, "linkedin.com/in/")]')

            if recruiter_elements:
                recruiter_element = recruiter_elements[0]
                recruiter_link = recruiter_element.get_attribute('href')
                logger.debug(f"Đã lấy được liên kết người tuyển dụng: {recruiter_link}")
                return recruiter_link
            else:
                logger.debug("Không tìm thấy liên kết người tuyển dụng trong phần thông tin đội ngũ tuyển dụng")
                return ""
        except Exception as e:
            logger.warning(f"Không thể lấy thông tin người tuyển dụng: {e}")
            return ""

    def _scroll_page(self) -> None:
        logger.debug("Đang cuộn trang")
        scrollable_element = self.driver.find_element(By.TAG_NAME, 'html')
        utils.scroll_slow(self.driver, scrollable_element, step=300, reverse=False)
        utils.scroll_slow(self.driver, scrollable_element, step=300, reverse=True)

    def _fill_application_form(self, job):
        logger.debug(f"Đang điền form ứng tuyển cho công việc: {job}")
        while True:
            self.fill_up(job)
            if self._next_or_submit():
                logger.debug("Đã gửi form ứng tuyển")
                break

    def _next_or_submit(self):
        logger.debug("Đang nhấp vào nút 'Tiếp theo' hoặc 'Gửi'")
        next_button = self.driver.find_element(By.CLASS_NAME, "artdeco-button--primary")
        button_text = next_button.text.lower()
        if 'submit application' in button_text:
            logger.debug("Đã tìm thấy nút Gửi, đang gửi ứng tuyển")
            self._unfollow_company()
            time.sleep(random.uniform(1.5, 2.5))
            next_button.click()
            time.sleep(random.uniform(1.5, 2.5))
            return True
        time.sleep(random.uniform(1.5, 2.5))
        next_button.click()
        time.sleep(random.uniform(3.0, 5.0))
        self._check_for_errors()

    def _unfollow_company(self) -> None:
        try:
            logger.debug("Đang bỏ theo dõi công ty")
            follow_checkbox = self.driver.find_element(
                By.XPATH, "//label[contains(.,'to stay up to date with their page.')]")
            follow_checkbox.click()
        except Exception as e:
            logger.debug(f"Không thể bỏ theo dõi công ty: {e}")

    def _check_for_errors(self) -> None:
        logger.debug("Đang kiểm tra lỗi form")
        error_elements = self.driver.find_elements(By.CLASS_NAME, 'artdeco-inline-feedback--error')
        if error_elements:
            logger.error(f"Gửi form thất bại với các lỗi: {error_elements}")
            raise Exception(f"Không thể trả lời hoặc tải lên file. {str([e.text for e in error_elements])}")

    def _discard_application(self) -> None:
        logger.debug("Đang hủy ứng tuyển")
        try:
            self.driver.find_element(By.CLASS_NAME, 'artdeco-modal__dismiss').click()
            time.sleep(random.uniform(3, 5))
            self.driver.find_elements(By.CLASS_NAME, 'artdeco-modal__confirm-dialog-btn')[0].click()
            time.sleep(random.uniform(3, 5))
        except Exception as e:
            logger.warning(f"Không thể hủy ứng tuyển: {e}")

    def fill_up(self, job) -> None:
        logger.debug(f"Đang điền các phần của form cho công việc: {job}")

        try:
            easy_apply_content = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'jobs-easy-apply-content'))
            )

            pb4_elements = easy_apply_content.find_elements(By.CLASS_NAME, 'pb4')
            for element in pb4_elements:
                self._process_form_element(element, job)
        except Exception as e:
            logger.error(f"Không thể tìm thấy các phần tử của form: {e}")

    def _process_form_element(self, element: WebElement, job) -> None:
        logger.debug("Đang xử lý phần tử form")
        if self._is_upload_field(element):
            self._handle_upload_fields(element, job)
        else:
            self._fill_additional_questions()

    def _handle_dropdown_fields(self, element: WebElement) -> None:
        logger.debug("Đang xử lý các trường dropdown")

        dropdown = element.find_element(By.TAG_NAME, 'select')
        select = Select(dropdown)

        options = [option.text for option in select.options]
        logger.debug(f"Đã tìm thấy các tùy chọn dropdown: {options}")

        parent_element = dropdown.find_element(By.XPATH, '../..')

        label_elements = parent_element.find_elements(By.TAG_NAME, 'label')
        if label_elements:
            question_text = label_elements[0].text.lower()
        else:
            question_text = "unknown"

        logger.debug(f"Đã phát hiện văn bản câu hỏi: {question_text}")

        existing_answer = None
        for item in self.all_data:
            if self._sanitize_text(question_text) in item['question'] and item['type'] == 'dropdown':
                existing_answer = item['answer']
                break

        if existing_answer:
            logger.debug(f"Đã tìm thấy câu trả lời có sẵn cho câu hỏi '{question_text}': {existing_answer}")
        else:
            # Nếu không có câu trả lời có sẵn, hỏi mô hình
            logger.debug(f"Không tìm thấy câu trả lời có sẵn, đang hỏi mô hình cho: {question_text}")
            existing_answer = self.gpt_answerer.answer_question_from_options(question_text, options)
            logger.debug(f"Mô hình đã cung cấp câu trả lời: {existing_answer}")
            self._save_questions_to_json({'type': 'dropdown', 'question': question_text, 'answer': existing_answer})

        if existing_answer in options:
            select.select_by_visible_text(existing_answer)
            logger.debug(f"Đã chọn tùy chọn: {existing_answer}")
        else:
            logger.error(f"Câu trả lời '{existing_answer}' không phải là một tùy chọn hợp lệ trong dropdown")
            raise Exception(f"Đã chọn tùy chọn không hợp lệ: {existing_answer}")

    def _is_upload_field(self, element: WebElement) -> bool:
        is_upload = bool(element.find_elements(By.XPATH, ".//input[@type='file']"))
        logger.debug(f"Phần tử là trường tải lên: {is_upload}")
        return is_upload

    def _handle_upload_fields(self, element: WebElement, job) -> None:
        logger.debug("Đang xử lý các trường tải lên")

        try:
            show_more_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Show more resumes')]")
            show_more_button.click()
            logger.debug("Đã nhấp vào nút 'Hiển thị thêm CV'")
        except NoSuchElementException:
            logger.debug("Không tìm thấy nút 'Hiển thị thêm CV', tiếp tục...")

        file_upload_elements = self.driver.find_elements(By.XPATH, "//input[@type='file']")
        for element in file_upload_elements:
            parent = element.find_element(By.XPATH, "..")
            self.driver.execute_script("arguments[0].classList.remove('hidden')", element)

            output = self.gpt_answerer.resume_or_cover(parent.text.lower())
            if 'resume' in output:
                logger.debug("Đang tải lên CV")
                if self.resume_path is not None and self.resume_path.resolve().is_file():
                    element.send_keys(str(self.resume_path.resolve()))
                    logger.debug(f"Đã tải lên CV từ đường dẫn: {self.resume_path.resolve()}")
                else:
                    logger.debug("Không tìm thấy đường dẫn CV hoặc không hợp lệ, đang tạo CV mới")
                    self._create_and_upload_resume(element, job)
            elif 'cover' in output:
                logger.debug("Đang tải lên thư xin việc")
                self._create_and_upload_cover_letter(element, job)

        logger.debug("Đã hoàn thành xử lý các trường tải lên")

    def _create_and_upload_resume(self, element, job):
        logger.debug("Bắt đầu quá trình tạo và tải lên CV.")
        folder_path = 'generated_cv'

        try:
            if not os.path.exists(folder_path):
                logger.debug(f"Đang tạo thư mục tại đường dẫn: {folder_path}")
            os.makedirs(folder_path, exist_ok=True)
        except Exception as e:
            logger.error(f"Không thể tạo thư mục: {folder_path}. Lỗi: {e}")
            raise

        while True:
            try:
                timestamp = int(time.time())
                file_path_pdf = os.path.join(folder_path, f"CV_{timestamp}.pdf")
                logger.debug(f"Đã tạo đường dẫn file cho CV: {file_path_pdf}")

                logger.debug(f"Đang tạo CV cho công việc: {job.title} tại {job.company}")
                resume_pdf_base64 = self.resume_generator_manager.pdf_base64(job_description_text=job.description)
                with open(file_path_pdf, "xb") as f:
                    f.write(base64.b64decode(resume_pdf_base64))
                logger.debug(f"CV đã được tạo thành công và lưu tại: {file_path_pdf}")

                break
            except HTTPStatusError as e:
                if e.response.status_code == 429:
                    # Xử lý lỗi giới hạn tốc độ
                    retry_after = e.response.headers.get('retry-after')
                    retry_after_ms = e.response.headers.get('retry-after-ms')

                    if retry_after:
                        wait_time = int(retry_after)
                        logger.warning(f"Đã vượt quá giới hạn tốc độ, đợi {wait_time} giây trước khi thử lại...")
                    elif retry_after_ms:
                        wait_time = int(retry_after_ms) / 1000.0
                        logger.warning(f"Đã vượt quá giới hạn tốc độ, đợi {wait_time} mili giây trước khi thử lại...")
                    else:
                        wait_time = 20
                        logger.warning(f"Đã vượt quá giới hạn tốc độ, đợi {wait_time} giây trước khi thử lại...")

                    time.sleep(wait_time)
                else:
                    logger.error(f"Lỗi HTTP: {e}")
                    raise

            except Exception as e:
                logger.error(f"Không thể tạo CV: {e}")
                tb_str = traceback.format_exc()
                logger.error(f"Traceback: {tb_str}")
                if "RateLimitError" in str(e):
                    logger.warning("Gặp lỗi giới hạn tốc độ, đang thử lại...")
                    time.sleep(20)
                else:
                    raise

        file_size = os.path.getsize(file_path_pdf)
        max_file_size = 2 * 1024 * 1024  # 2 MB
        logger.debug(f"Kích thước file CV: {file_size} bytes")
        if file_size > max_file_size:
            logger.error(f"Kích thước file CV vượt quá 2 MB: {file_size} bytes")
            raise ValueError("Kích thước file CV vượt quá giới hạn tối đa 2 MB.")

        allowed_extensions = {'.pdf', '.doc', '.docx'}
        file_extension = os.path.splitext(file_path_pdf)[1].lower()
        logger.debug(f"Phần mở rộng file CV: {file_extension}")
        if file_extension not in allowed_extensions:
            logger.error(f"Định dạng file CV không hợp lệ: {file_extension}")
            raise ValueError("Định dạng file CV không được phép. Chỉ hỗ trợ các định dạng PDF, DOC và DOCX.")

        try:
            logger.debug(f"Đang tải lên CV từ đường dẫn: {file_path_pdf}")
            element.send_keys(os.path.abspath(file_path_pdf))
            job.pdf_path = os.path.abspath(file_path_pdf)
            time.sleep(2)
            logger.debug(f"CV đã được tạo và tải lên thành công: {file_path_pdf}")
        except Exception as e:
            tb_str = traceback.format_exc()
            logger.error(f"Tải lên CV thất bại: {tb_str}")
            raise Exception(f"Tải lên thất bại: \nTraceback:\n{tb_str}")

    def _create_and_upload_cover_letter(self, element: WebElement, job) -> None:
        logger.debug("Bắt đầu quá trình tạo và tải lên thư xin việc.")

        cover_letter_text = self.gpt_answerer.answer_question_textual_wide_range("Viết một thư xin việc")

        folder_path = 'generated_cv'

        try:
            # Tạo thư mục nếu chưa tồn tại
            if not os.path.exists(folder_path):
                logger.debug(f"Đang tạo thư mục tại đường dẫn: {folder_path}")
            os.makedirs(folder_path, exist_ok=True)
        except Exception as e:
            logger.error(f"Không thể tạo thư mục: {folder_path}. Lỗi: {e}")
            raise

        while True:
            try:
                timestamp = int(time.time())
                file_path_pdf = os.path.join(folder_path, f"Cover_Letter_{timestamp}.pdf")
                logger.debug(f"Đã tạo đường dẫn file cho thư xin việc: {file_path_pdf}")

                c = canvas.Canvas(file_path_pdf, pagesize=A4)

                # Lấy kích thước trang A4
                page_width, page_height = A4
                # Tạo đối tượng text bắt đầu từ vị trí (50, page_height - 50)
                text_object = c.beginText(50, page_height - 50)
                # Đặt font chữ là Helvetica với kích thước 12
                text_object.setFont("Helvetica", 12)

                # Đặt chiều rộng tối đa cho văn bản
                max_width = page_width - 100
                # Đặt lề dưới
                bottom_margin = 50
                # Tính chiều cao khả dụng cho văn bản
                available_height = page_height - bottom_margin - 50

                # Hàm chia văn bản thành các dòng phù hợp với chiều rộng trang
                def split_text_by_width(text, font, font_size, max_width):
                    wrapped_lines = []
                    for line in text.splitlines():
                        # Kiểm tra nếu chiều rộng dòng vượt quá max_width
                        if utils.stringWidth(line, font, font_size) > max_width:
                            words = line.split()
                            new_line = ""
                            for word in words:
                                # Thêm từ vào dòng nếu không vượt quá max_width
                                if utils.stringWidth(new_line + word + " ", font, font_size) <= max_width:
                                    new_line += word + " "
                                else:
                                    # Nếu vượt quá, thêm dòng hiện tại vào kết quả và bắt đầu dòng mới
                                    wrapped_lines.append(new_line.strip())
                                    new_line = word + " "
                            wrapped_lines.append(new_line.strip())
                        else:
                            wrapped_lines.append(line)
                    return wrapped_lines

                # Chia văn bản thành các dòng
                lines = split_text_by_width(cover_letter_text, "Helvetica", 12, max_width)

                # Vẽ từng dòng văn bản
                for line in lines:
                    text_height = text_object.getY()
                    if text_height > bottom_margin:
                        # Nếu còn đủ không gian, thêm dòng vào trang hiện tại
                        text_object.textLine(line)
                    else:
                        # Nếu không đủ không gian, vẽ văn bản hiện tại và tạo trang mới
                        c.drawText(text_object)
                        c.showPage()
                        text_object = c.beginText(50, page_height - 50)
                        text_object.setFont("Helvetica", 12)
                        text_object.textLine(line)

                # Vẽ văn bản cuối cùng và lưu file PDF
                c.drawText(text_object)
                c.save()
                logger.debug(f"Thư xin việc đã được tạo và lưu thành công tại: {file_path_pdf}")

                break
            except Exception as e:
                logger.error(f"Không thể tạo thư xin việc: {e}")
                tb_str = traceback.format_exc()
                logger.error(f"Traceback: {tb_str}")
                raise

        # Kiểm tra kích thước file
        file_size = os.path.getsize(file_path_pdf)
        max_file_size = 2 * 1024 * 1024  # 2 MB
        logger.debug(f"Kích thước file thư xin việc: {file_size} bytes")
        if file_size > max_file_size:
            logger.error(f"Kích thước file thư xin việc vượt quá 2 MB: {file_size} bytes")
            raise ValueError("Kích thước file thư xin việc vượt quá giới hạn tối đa 2 MB.")

        # Kiểm tra phần mở rộng file
        allowed_extensions = {'.pdf', '.doc', '.docx'}
        file_extension = os.path.splitext(file_path_pdf)[1].lower()
        logger.debug(f"Phần mở rộng file thư xin việc: {file_extension}")
        if file_extension not in allowed_extensions:
            logger.error(f"Định dạng file thư xin việc không hợp lệ: {file_extension}")
            raise ValueError("Định dạng file thư xin việc không được phép. Chỉ hỗ trợ các định dạng PDF, DOC và DOCX.")

        try:
            # Tải lên thư xin việc
            logger.debug(f"Đang tải lên thư xin việc từ đường dẫn: {file_path_pdf}")
            element.send_keys(os.path.abspath(file_path_pdf))
            job.cover_letter_path = os.path.abspath(file_path_pdf)
            time.sleep(2)
            logger.debug(f"Thư xin việc đã được tạo và tải lên thành công: {file_path_pdf}")
        except Exception as e:
            tb_str = traceback.format_exc()
            logger.error(f"Tải lên thư xin việc thất bại: {tb_str}")
            raise Exception(f"Tải lên thất bại: \nTraceback:\n{tb_str}")

    def _fill_additional_questions(self) -> None:
        logger.debug("Đang điền các câu hỏi bổ sung")
        form_sections = self.driver.find_elements(By.CLASS_NAME, 'jobs-easy-apply-form-section__grouping')
        for section in form_sections:
            self._process_form_section(section)

    def _process_form_section(self, section: WebElement) -> None:
        logger.debug("Đang xử lý phần form")
        if self._handle_terms_of_service(section):
            logger.debug("Đã xử lý điều khoản dịch vụ")
            return
        if self._find_and_handle_radio_question(section):
            logger.debug("Đã xử lý câu hỏi radio")
            return
        if self._find_and_handle_textbox_question(section):
            logger.debug("Đã xử lý câu hỏi textbox")
            return
        if self._find_and_handle_date_question(section):
            logger.debug("Đã xử lý câu hỏi ngày tháng")
            return

        if self._find_and_handle_dropdown_question(section):
            logger.debug("Đã xử lý câu hỏi dropdown")
            return

    def _handle_terms_of_service(self, element: WebElement) -> bool:
        checkbox = element.find_elements(By.TAG_NAME, 'label')
        if checkbox and any(
                term in checkbox[0].text.lower() for term in ['terms of service', 'privacy policy', 'terms of use']):
            checkbox[0].click()
            logger.debug("Đã nhấp vào ô checkbox điều khoản dịch vụ")
            return True
        return False

    def _find_and_handle_radio_question(self, section: WebElement) -> bool:
        question = section.find_element(By.CLASS_NAME, 'jobs-easy-apply-form-element')
        radios = question.find_elements(By.CLASS_NAME, 'fb-text-selectable__option')
        if radios:
            question_text = section.text.lower()
            options = [radio.text.lower() for radio in radios]

            existing_answer = None
            for item in self.all_data:
                if self._sanitize_text(question_text) in item['question'] and item['type'] == 'radio':
                    existing_answer = item

                    break
            if existing_answer:
                self._select_radio(radios, existing_answer['answer'])
                logger.debug("Đã chọn câu trả lời radio có sẵn")
                return True

            answer = self.gpt_answerer.answer_question_from_options(question_text, options)
            self._save_questions_to_json({'type': 'radio', 'question': question_text, 'answer': answer})
            self._select_radio(radios, answer)
            logger.debug("Đã chọn câu trả lời radio mới")
            return True
        return False

    def _find_and_handle_textbox_question(self, section: WebElement) -> bool:
        logger.debug("Đang tìm kiếm các trường văn bản trong phần.")
        text_fields = section.find_elements(By.TAG_NAME, 'input') + section.find_elements(By.TAG_NAME, 'textarea')

        if text_fields:
            text_field = text_fields[0]
            question_text = section.find_element(By.TAG_NAME, 'label').text.lower().strip()
            logger.debug(f"Đã tìm thấy trường văn bản với nhãn: {question_text}")

            is_numeric = self._is_numeric_field(text_field)
            logger.debug(f"Trường này có phải là số? {'Có' if is_numeric else 'Không'}")

            question_type = 'numeric' if is_numeric else 'textbox'

            # Kiểm tra xem có phải là trường thư xin việc không (không phân biệt chữ hoa/thường)
            is_cover_letter = 'cover letter' in question_text.lower()

            # Tìm câu trả lời có sẵn nếu không phải là trường thư xin việc
            existing_answer = None
            if not is_cover_letter:
                for item in self.all_data:
                    if self._sanitize_text(item['question']) == self._sanitize_text(question_text) and item.get('type') == question_type:
                        existing_answer = item['answer']
                        logger.debug(f"Đã tìm thấy câu trả lời có sẵn: {existing_answer}")
                        break

            if existing_answer and not is_cover_letter:
                answer = existing_answer
                logger.debug(f"Sử dụng câu trả lời có sẵn: {answer}")
            else:
                if is_numeric:
                    answer = self.gpt_answerer.answer_question_numeric(question_text)
                    logger.debug(f"Đã tạo câu trả lời số: {answer}")
                else:
                    answer = self.gpt_answerer.answer_question_textual_wide_range(question_text)
                    logger.debug(f"Đã tạo câu trả lời văn bản: {answer}")

            self._enter_text(text_field, answer)
            logger.debug("Đã nhập câu trả lời vào trường văn bản.")

            # Lưu câu trả lời không phải thư xin việc
            if not is_cover_letter:
                self._save_questions_to_json({'type': question_type, 'question': question_text, 'answer': answer})
                logger.debug("Đã lưu câu trả lời không phải thư xin việc vào JSON.")

            time.sleep(1)
            text_field.send_keys(Keys.ARROW_DOWN)
            text_field.send_keys(Keys.ENTER)
            logger.debug("Đã chọn tùy chọn đầu tiên từ dropdown.")
            return True

        logger.debug("Không tìm thấy trường văn bản nào trong phần.")
        return False

    def _find_and_handle_date_question(self, section: WebElement) -> bool:
        date_fields = section.find_elements(By.CLASS_NAME, 'artdeco-datepicker__input')
        if date_fields:
            date_field = date_fields[0]
            question_text = section.text.lower()
            answer_date = self.gpt_answerer.answer_question_date()
            answer_text = answer_date.strftime("%Y-%m-%d")

            existing_answer = None
            for item in self.all_data:
                if self._sanitize_text(question_text) in item['question'] and item['type'] == 'date':
                    existing_answer = item

                    break
            if existing_answer:
                self._enter_text(date_field, existing_answer['answer'])
                logger.debug("Đã nhập câu trả lời ngày tháng có sẵn")
                return True

            self._save_questions_to_json({'type': 'date', 'question': question_text, 'answer': answer_text})
            self._enter_text(date_field, answer_text)
            logger.debug("Đã nhập câu trả lời ngày tháng mới")
            return True
        return False

    def _find_and_handle_dropdown_question(self, section: WebElement) -> bool:
        try:
            question = section.find_element(By.CLASS_NAME, 'jobs-easy-apply-form-element')

            dropdowns = question.find_elements(By.TAG_NAME, 'select')
            if not dropdowns:
                dropdowns = section.find_elements(By.CSS_SELECTOR, '[data-test-text-entity-list-form-select]')

            if dropdowns:
                dropdown = dropdowns[0]
                select = Select(dropdown)
                options = [option.text for option in select.options]

                logger.debug(f"Đã tìm thấy các tùy chọn dropdown: {options}")

                question_text = question.find_element(By.TAG_NAME, 'label').text.lower()
                logger.debug(f"Đang xử lý câu hỏi dropdown hoặc combobox: {question_text}")

                current_selection = select.first_selected_option.text
                logger.debug(f"Lựa chọn hiện tại: {current_selection}")

                existing_answer = None
                for item in self.all_data:
                    if self._sanitize_text(question_text) in item['question'] and item['type'] == 'dropdown':
                        existing_answer = item['answer']
                        break

                if existing_answer:
                    logger.debug(f"Đã tìm thấy câu trả lời có sẵn cho câu hỏi '{question_text}': {existing_answer}")
                    if current_selection != existing_answer:
                        logger.debug(f"Đang cập nhật lựa chọn thành: {existing_answer}")
                        self._select_dropdown_option(dropdown, existing_answer)
                    return True

                logger.debug(f"Không tìm thấy câu trả lời có sẵn, đang truy vấn mô hình cho: {question_text}")

                answer = self.gpt_answerer.answer_question_from_options(question_text, options)
                self._save_questions_to_json({'type': 'dropdown', 'question': question_text, 'answer': answer})
                self._select_dropdown_option(dropdown, answer)
                logger.debug(f"Đã chọn câu trả lời dropdown mới: {answer}")
                return True

            else:
                # Ghi log các phần tử để gỡ lỗi
                logger.debug(f"Không tìm thấy dropdown. Đang ghi log các phần tử để gỡ lỗi.")
                elements = section.find_elements(By.XPATH, ".//*")
                logger.debug(f"Các phần tử được tìm thấy: {[element.tag_name for element in elements]}")
                return False

        except Exception as e:
            logger.warning(f"Không thể xử lý câu hỏi dropdown hoặc combobox: {e}", exc_info=True)
            return False

    def _is_numeric_field(self, field: WebElement) -> bool:
        field_type = field.get_attribute('type').lower()
        field_id = field.get_attribute("id").lower()
        is_numeric = 'numeric' in field_id or field_type == 'number' or ('text' == field_type and 'numeric' in field_id)
        logger.debug(f"Loại trường: {field_type}, ID trường: {field_id}, Là số: {is_numeric}")
        return is_numeric

    def _enter_text(self, element: WebElement, text: str) -> None:
        logger.debug(f"Đang nhập văn bản: {text}")
        element.clear()
        element.send_keys(text)

    def _select_radio(self, radios: List[WebElement], answer: str) -> None:
        logger.debug(f"Đang chọn tùy chọn radio: {answer}")
        for radio in radios:
            if answer in radio.text.lower():
                radio.find_element(By.TAG_NAME, 'label').click()
                return
        radios[-1].find_element(By.TAG_NAME, 'label').click()

    def _select_dropdown_option(self, element: WebElement, text: str) -> None:
        logger.debug(f"Đang chọn tùy chọn dropdown: {text}")
        select = Select(element)
        select.select_by_visible_text(text)

    def _save_questions_to_json(self, question_data: dict) -> None:
        output_file = 'answers.json'
        question_data['question'] = self._sanitize_text(question_data['question'])
        logger.debug(f"Đang lưu dữ liệu câu hỏi vào JSON: {question_data}")
        try:
            try:
                with open(output_file, 'r') as f:
                    try:
                        data = json.load(f)
                        if not isinstance(data, list):
                            raise ValueError("Định dạng file JSON không chính xác. Cần một danh sách các câu hỏi.")
                    except json.JSONDecodeError:
                        logger.error("Giải mã JSON thất bại")
                        data = []
            except FileNotFoundError:
                logger.warning("Không tìm thấy file JSON, đang tạo file mới")
                data = []
            data.append(question_data)
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=4)
            logger.debug("Dữ liệu câu hỏi đã được lưu thành công vào JSON")
        except Exception:
            tb_str = traceback.format_exc()
            logger.error(f"Lỗi khi lưu dữ liệu câu hỏi vào file JSON: {tb_str}")
            raise Exception(f"Lỗi khi lưu dữ liệu câu hỏi vào file JSON: \nTraceback:\n{tb_str}")

    def _sanitize_text(self, text: str) -> str:
        sanitized_text = text.lower().strip().replace('"', '').replace('\\', '')
        sanitized_text = re.sub(r'[\x00-\x1F\x7F]', '', sanitized_text).replace('\n', ' ').replace('\r', '').rstrip(',')
        logger.debug(f"Văn bản đã được làm sạch: {sanitized_text}")
        return sanitized_text