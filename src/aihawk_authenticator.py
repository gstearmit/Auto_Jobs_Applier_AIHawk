import random
import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException, TimeoutException, UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from loguru import logger


class AIHawkAuthenticator:

    def __init__(self, driver=None):
        # Khởi tạo đối tượng với trình duyệt được cung cấp
        self.driver = driver
        logger.debug(f"AIHawkAuthenticator được khởi tạo với trình duyệt: {driver}")

    def start(self):
        # Bắt đầu quá trình đăng nhập
        logger.info("Khởi động trình duyệt Chrome để đăng nhập vào AIHawk.")
        if self.is_logged_in():
            logger.info("Người dùng đã đăng nhập. Bỏ qua quá trình đăng nhập.")
            return
        else:
            logger.info("Người dùng chưa đăng nhập. Tiến hành đăng nhập.")
            self.handle_login()

    def handle_login(self):
        # Xử lý quá trình đăng nhập
        logger.info("Điều hướng đến trang đăng nhập AIHawk...")
        self.driver.get("https://www.linkedin.com/login")
        if 'feed' in self.driver.current_url:
            logger.debug("Người dùng đã đăng nhập.")
            return
        try:
            self.enter_credentials()
        except NoSuchElementException as e:
            logger.error(f"Không thể đăng nhập vào AIHawk. Không tìm thấy phần tử: {e}")
        self.handle_security_check()


    def enter_credentials(self):
        try:
            logger.debug("Nhập thông tin đăng nhập...")
            
            check_interval = 4  # Khoảng thời gian để ghi lại URL hiện tại
            elapsed_time = 0

            while True:
                # Ghi lại URL hiện tại mỗi 4 giây và nhắc người dùng đăng nhập
                current_url = self.driver.current_url
                logger.info(f"Vui lòng đăng nhập tại {current_url}")

                # Kiểm tra xem người dùng đã ở trang feed chưa
                if 'feed' in current_url:
                    logger.debug("Đăng nhập thành công, đã chuyển hướng đến trang feed.")
                    break
                else:
                    # Tùy chọn chờ trường mật khẩu (hoặc bất kỳ phần tử nào khác bạn mong đợi trên trang đăng nhập)
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "password"))
                    )
                    logger.debug("Đã phát hiện trường mật khẩu, đang chờ hoàn tất đăng nhập.")

                time.sleep(check_interval)
                elapsed_time += check_interval

        except TimeoutException:
            logger.error("Không tìm thấy biểu mẫu đăng nhập. Hủy bỏ đăng nhập.")


    def handle_security_check(self):
        # Xử lý kiểm tra bảo mật nếu cần
        try:
            logger.debug("Xử lý kiểm tra bảo mật...")
            WebDriverWait(self.driver, 10).until(
                EC.url_contains('https://www.linkedin.com/checkpoint/challengesV2/')
            )
            logger.warning("Đã phát hiện điểm kiểm tra bảo mật. Vui lòng hoàn thành thử thách.")
            WebDriverWait(self.driver, 300).until(
                EC.url_contains('https://www.linkedin.com/feed/')
            )
            logger.info("Kiểm tra bảo mật đã hoàn tất")
        except TimeoutException:
            logger.error("Kiểm tra bảo mật chưa hoàn tất. Vui lòng thử lại sau.")

    def is_logged_in(self):
        # Kiểm tra xem người dùng đã đăng nhập chưa
        try:
            self.driver.get('https://www.linkedin.com/feed')
            logger.debug("Kiểm tra xem người dùng đã đăng nhập chưa...")
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'share-box-feed-entry__trigger'))
            )

            # Kiểm tra sự hiện diện của nút "Bắt đầu bài đăng"
            buttons = self.driver.find_elements(By.CLASS_NAME, 'share-box-feed-entry__trigger')
            logger.debug(f"Đã tìm thấy {len(buttons)} nút 'Bắt đầu bài đăng'")

            for i, button in enumerate(buttons):
                logger.debug(f"Nút {i + 1} có nội dung: {button.text.strip()}")

            if any(button.text.strip().lower() == 'start a post' for button in buttons):
                logger.info("Đã tìm thấy nút 'Bắt đầu bài đăng' cho thấy người dùng đã đăng nhập.")
                return True

            profile_img_elements = self.driver.find_elements(By.XPATH, "//img[contains(@alt, 'Photo of')]")
            if profile_img_elements:
                logger.info("Đã tìm thấy ảnh hồ sơ. Giả định người dùng đã đăng nhập.")
                return True

            logger.info("Không tìm thấy nút 'Bắt đầu bài đăng' hoặc ảnh hồ sơ. Người dùng có thể chưa đăng nhập.")
            return False

        except TimeoutException:
            logger.error("Các phần tử trang mất quá nhiều thời gian để tải hoặc không được tìm thấy.")
            return False