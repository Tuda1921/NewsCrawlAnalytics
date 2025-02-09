import requests
from bs4 import BeautifulSoup
import csv
import os
import re
import random
import unidecode
import time

# Danh sách User-Agent để sử dụng
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
]

def random_delay(min_delay, max_delay):
    """Trả về thời gian trễ ngẫu nhiên để tránh bị chặn bởi Google."""
    return random.uniform(min_delay, max_delay)

def slug(text):
    """Chuyển đổi ký tự tiếng Việt thành ASCII và định dạng dưới dạng slug."""
    text = unidecode.unidecode(text)  # Chuyển đổi thành ASCII
    text = text.lower()  # Chuyển đổi thành chữ thường
    text = re.sub(r'\s+', '-', text)  # Thay thế khoảng trắng bằng dấu gạch ngang
    text = re.sub(r'[^\w\-]', '', text)  # Loại bỏ ký tự không phải là chữ và số, trừ dấu gạch ngang
    return text

def extract_google_results(keywords, site, start_year, end_year,
                           min_delay, max_delay,
                           output_dir="Google_Search_Results", output_file="results.csv", page_limit=200,
                           log_callback=None):
    params = {
        "hl": "vi",  # Ngôn ngữ đặt thành tiếng Việt
        "gl": "vn",  # Quốc gia đặt thành Việt Nam
        "start": 0   # Bắt đầu từ trang kết quả đầu tiên
    }

    headers = {
        "User-Agent": USER_AGENTS[0]  # User-Agent ban đầu
    }

    # Tạo thư mục lưu trữ kết quả và tệp CSV
    os.makedirs(output_dir, exist_ok=True)
    csv_file = os.path.join(output_dir, output_file)

    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as csvfile:
        fieldnames = ['keyword', 'title', 'link', 'date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for keyword in keywords:
            page_num = 0
            params["q"] = f"intitle:{keyword} site:{site}"  # Truy vấn tìm kiếm với giới hạn trang web

            while page_num < page_limit:
                page_num += 1
                if log_callback:
                    log_callback(f"Đang lấy trang: {page_num} cho từ khóa '{keyword}'")

                # Gửi yêu cầu đến Google Search
                response = requests.get("https://www.google.com/search", params=params, headers=headers, timeout=30)

                if response.status_code != 200:
                    if log_callback:
                        log_callback(f"Không thể truy xuất trang {page_num}. Mã trạng thái: {response.status_code}")
                    break

                soup = BeautifulSoup(response.text, 'lxml')

                # Kiểm tra nếu không có kết quả nào
                if not soup.select(".tF2Cxc"):
                    if log_callback:
                        log_callback(f"Không tìm thấy kết quả nào cho từ khóa '{keyword}'.")
                    break

                # Phân tích kết quả tìm kiếm
                for result in soup.select(".tF2Cxc"):
                    title = result.select_one(".DKV0Md").text
                    snippet = result.select_one(".VwiC3b").text if result.select_one(".VwiC3b") else None
                    link = result.select_one(".yuRUbf a")["href"]

                    # Trích xuất ngày từ đoạn đầu của snippet
                    date = "Không có ngày"  # Giá trị mặc định nếu không có ngày
                    if snippet:
                        # Regex để bắt ngày theo định dạng "15 thg 11, 2023"
                        date_match = re.match(r'(\d{1,2})\s+thg\s+(\d{1,2}),\s+(\d{4})', snippet)
                        if date_match:
                            day = date_match.group(1)
                            month = date_match.group(2)
                            year = date_match.group(3)
                            date = f"{day}/{month}/{year}"

                            # Kiểm tra nếu năm nằm trong phạm vi mong muốn
                            if not (start_year <= int(year) <= end_year):
                                continue

                    # Lưu kết quả nếu liên kết chứa slug của từ khóa
                    if slug(keyword) in link.lower():
                        result_data = {
                            "keyword": keyword,
                            "title": title,
                            "link": link,
                            "date": date
                        }
                        writer.writerow(result_data)
                        if log_callback:
                            log_callback(f"Đã ghi vào CSV: {result_data['title']} - {result_data['link']}")

                # Tăng số trang tìm kiếm
                params["start"] += 10
                time.sleep(random.uniform(min_delay, max_delay))

    if log_callback:
        log_callback(f"Hoàn tất tìm kiếm cho tất cả các từ khóa.")
