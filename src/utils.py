import logging  # Thư viện để ghi log
import os  # Thư viện để làm việc với hệ thống tệp
import random  # Thư viện để tạo số ngẫu nhiên
import sys  # Thư viện để tương tác với hệ thống
import time  # Thư viện để làm việc với thời gian

from selenium import webdriver  # Thư viện Selenium để tự động hóa trình duyệt
from loguru import logger  # Thư viện loguru để ghi log

from app_config import MINIMUM_LOG_LEVEL  # Nhập mức độ log tối thiểu từ cấu hình ứng dụng

log_file = "app_log.log"  # Tên file log

# Kiểm tra mức độ log hợp lệ và thiết lập logger
if MINIMUM_LOG_LEVEL in ["DEBUG", "TRACE", "INFO", "WARNING", "ERROR", "CRITICAL"]:
    logger.remove()  # Xóa logger mặc định
    logger.add(sys.stderr, level=MINIMUM_LOG_LEVEL)  # Thêm logger mới với mức độ đã chỉ định
else:
    logger.warning(f"Invalid log level: {MINIMUM_LOG_LEVEL}. Defaulting to DEBUG.")  # Cảnh báo nếu mức độ không hợp lệ
    logger.remove()  # Xóa logger mặc định
    logger.add(sys.stderr, level="DEBUG")  # Thiết lập mức độ log mặc định là DEBUG

# Đường dẫn đến profile Chrome
chromeProfilePath = os.path.join(os.getcwd(), "chrome_profile", "linkedin_profile")

def ensure_chrome_profile():
    """Đảm bảo rằng profile Chrome tồn tại tại đường dẫn đã chỉ định."""
    logger.debug(f"Ensuring Chrome profile exists at path: {chromeProfilePath}")  # Ghi log thông tin
    profile_dir = os.path.dirname(chromeProfilePath)  # Lấy thư mục chứa profile
    if not os.path.exists(profile_dir):  # Kiểm tra xem thư mục có tồn tại không
        os.makedirs(profile_dir)  # Tạo thư mục nếu không tồn tại
        logger.debug(f"Created directory for Chrome profile: {profile_dir}")  # Ghi log thông tin
    if not os.path.exists(chromeProfilePath):  # Kiểm tra xem profile có tồn tại không
        os.makedirs(chromeProfilePath)  # Tạo profile nếu không tồn tại
        logger.debug(f"Created Chrome profile directory: {chromeProfilePath}")  # Ghi log thông tin
    return chromeProfilePath  # Trả về đường dẫn profile

def is_scrollable(element):
    """Kiểm tra xem phần tử có thể cuộn được hay không."""
    scroll_height = element.get_attribute("scrollHeight")  # Lấy chiều cao cuộn
    client_height = element.get_attribute("clientHeight")  # Lấy chiều cao của phần tử
    scrollable = int(scroll_height) > int(client_height)  # Kiểm tra khả năng cuộn
    logger.debug(f"Element scrollable check: scrollHeight={scroll_height}, clientHeight={client_height}, scrollable={scrollable}")  # Ghi log thông tin
    return scrollable  # Trả về kết quả kiểm tra

def scroll_slow(driver, scrollable_element, start=0, end=3600, step=300, reverse=False):
    """Cuộn chậm phần tử có thể cuộn."""
    logger.debug(f"Starting slow scroll: start={start}, end={end}, step={step}, reverse={reverse}")  # Ghi log thông tin

    if reverse:  # Nếu cuộn ngược
        start, end = end, start  # Đổi chỗ start và end
        step = -step  # Đảo ngược bước cuộn

    if step == 0:  # Kiểm tra giá trị bước
        logger.error("Step value cannot be zero.")  # Ghi log lỗi
        raise ValueError("Step cannot be zero.")  # Ném lỗi nếu bước bằng 0

    max_scroll_height = int(scrollable_element.get_attribute("scrollHeight"))  # Lấy chiều cao tối đa của phần tử
    current_scroll_position = int(float(scrollable_element.get_attribute("scrollTop")))  # Lấy vị trí cuộn hiện tại
    logger.debug(f"Max scroll height of the element: {max_scroll_height}")  # Ghi log thông tin
    logger.debug(f"Current scroll position: {current_scroll_position}")  # Ghi log thông tin

    if reverse:  # Nếu cuộn ngược
        if current_scroll_position < start:  # Nếu vị trí hiện tại nhỏ hơn start
            start = current_scroll_position  # Đặt start bằng vị trí hiện tại
        logger.debug(f"Adjusted start position for upward scroll: {start}")  # Ghi log thông tin
    else:  # Nếu cuộn xuôi
        if end > max_scroll_height:  # Nếu end lớn hơn chiều cao tối đa
            logger.warning(f"End value exceeds the scroll height. Adjusting end to {max_scroll_height}")  # Ghi log cảnh báo
            end = max_scroll_height  # Đặt end bằng chiều cao tối đa

    script_scroll_to = "arguments[0].scrollTop = arguments[1];"  # Script để cuộn đến vị trí

    try:
        if scrollable_element.is_displayed():  # Kiểm tra xem phần tử có hiển thị không
            if not is_scrollable(scrollable_element):  # Kiểm tra khả năng cuộn
                logger.warning("The element is not scrollable.")  # Ghi log cảnh báo
                return  # Kết thúc hàm nếu không cuộn được

            if (step > 0 and start >= end) or (step < 0 and start <= end):  # Kiểm tra điều kiện cuộn
                logger.warning("No scrolling will occur due to incorrect start/end values.")  # Ghi log cảnh báo
                return  # Kết thúc hàm nếu không cuộn được

            position = start  # Đặt vị trí bắt đầu
            previous_position = None  # Theo dõi vị trí trước đó để tránh cuộn trùng lặp
            while (step > 0 and position < end) or (step < 0 and position > end):  # Vòng lặp cuộn
                if position == previous_position:  # Nếu vị trí không thay đổi
                    logger.debug(f"Stopping scroll as position hasn't changed: {position}")  # Ghi log thông tin
                    break  # Kết thúc vòng lặp

                try:
                    driver.execute_script(script_scroll_to, scrollable_element, position)  # Thực thi script cuộn
                    logger.debug(f"Scrolled to position: {position}")  # Ghi log thông tin
                except Exception as e:  # Bắt lỗi
                    logger.error(f"Error during scrolling: {e}")  # Ghi log lỗi

                previous_position = position  # Cập nhật vị trí trước đó
                position += step  # Cập nhật vị trí cuộn

                # Giảm bước nhưng đảm bảo không đảo ngược hướng
                step = max(10, abs(step) - 10) * (-1 if reverse else 1)

                time.sleep(random.uniform(0.6, 1.5))  # Tạm dừng ngẫu nhiên giữa các lần cuộn

            # Đảm bảo vị trí cuộn cuối cùng là chính xác
            driver.execute_script(script_scroll_to, scrollable_element, end)  # Cuộn đến vị trí cuối cùng
            logger.debug(f"Scrolled to final position: {end}")  # Ghi log thông tin
            time.sleep(0.5)  # Tạm dừng một chút
        else:
            logger.warning("The element is not visible.")  # Ghi log cảnh báo nếu phần tử không hiển thị
    except Exception as e:  # Bắt lỗi
        logger.error(f"Exception occurred during scrolling: {e}")  # Ghi log lỗi

def chrome_browser_options():
    """Thiết lập các tùy chọn cho trình duyệt Chrome."""
    logger.debug("Setting Chrome browser options")  # Ghi log thông tin
    ensure_chrome_profile()  # Đảm bảo profile Chrome tồn tại
    options = webdriver.ChromeOptions()  # Tạo đối tượng tùy chọn cho Chrome
    options.add_argument("--start-maximized")  # Mở trình duyệt ở chế độ tối đa
    options.add_argument("--no-sandbox")  # Tắt chế độ sandbox
    options.add_argument("--disable-dev-shm-usage")  # Tắt sử dụng bộ nhớ chia sẻ
    options.add_argument("--ignore-certificate-errors")  # Bỏ qua lỗi chứng chỉ
    options.add_argument("--disable-extensions")  # Tắt các tiện ích mở rộng
    options.add_argument("--disable-gpu")  # Tắt GPU
    options.add_argument("window-size=1200x800")  # Đặt kích thước cửa sổ
    options.add_argument("--disable-background-timer-throttling")  # Tắt giới hạn thời gian nền
    options.add_argument("--disable-backgrounding-occluded-windows")  # Tắt nền cho các cửa sổ bị che khuất
    options.add_argument("--disable-translate")  # Tắt dịch tự động
    options.add_argument("--disable-popup-blocking")  # Tắt chặn popup
    options.add_argument("--no-first-run")  # Bỏ qua lần chạy đầu tiên
    options.add_argument("--no-default-browser-check")  # Bỏ qua kiểm tra trình duyệt mặc định
    options.add_argument("--disable-logging")  # Tắt ghi log
    options.add_argument("--disable-autofill")  # Tắt tự động điền
    options.add_argument("--disable-plugins")  # Tắt các plugin
    options.add_argument("--disable-animations")  # Tắt hoạt ảnh
    options.add_argument("--disable-cache")  # Tắt bộ nhớ cache
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])  # Loại trừ một số chuyển đổi

    # Thiết lập các tùy chọn cho hình ảnh và stylesheet
    prefs = {
        "profile.default_content_setting_values.images": 2,  # Tắt hình ảnh
        "profile.managed_default_content_settings.stylesheets": 2,  # Tắt stylesheet
    }
    options.add_experimental_option("prefs", prefs)  # Thêm tùy chọn vào đối tượng

    if len(chromeProfilePath) > 0:  # Nếu đường dẫn profile không rỗng
        initial_path = os.path.dirname(chromeProfilePath)  # Lấy thư mục chứa profile
        profile_dir = os.path.basename(chromeProfilePath)  # Lấy tên thư mục profile
        options.add_argument('--user-data-dir=' + initial_path)  # Thêm đường dẫn dữ liệu người dùng
        options.add_argument("--profile-directory=" + profile_dir)  # Thêm thư mục profile
        logger.debug(f"Using Chrome profile directory: {chromeProfilePath}")  # Ghi log thông tin
    else:
        options.add_argument("--incognito")  # Mở Chrome ở chế độ ẩn danh
        logger.debug("Using Chrome in incognito mode")  # Ghi log thông tin

    return options  # Trả về các tùy chọn đã thiết lập

def printred(text):
    """In văn bản màu đỏ."""
    red = "\033[91m"  # Mã màu đỏ
    reset = "\033[0m"  # Mã đặt lại màu
    logger.debug("Printing text in red: %s", text)  # Ghi log thông tin
    print(f"{red}{text}{reset}")  # In văn bản màu đỏ

def printyellow(text):
    """In văn bản màu vàng."""
    yellow = "\033[93m"  # Mã màu vàng
    reset = "\033[0m"  # Mã đặt lại màu
    logger.debug("Printing text in yellow: %s", text)  # Ghi log thông tin
    print(f"{yellow}{text}{reset}")  # In văn bản màu vàng

def stringWidth(text, font, font_size):
    """Tính chiều rộng của chuỗi văn bản."""
    bbox = font.getbbox(text)  # Lấy bounding box của văn bản
    return bbox[2] - bbox[0]  # Trả về chiều rộng của văn bản