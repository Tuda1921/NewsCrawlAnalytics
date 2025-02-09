import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QTextEdit, QLineEdit, QVBoxLayout, QPushButton, QFileDialog
from Crawl_file import extract_google_results

CONFIG_FILE = 'config.json'
from PyQt5.QtCore import QThread, pyqtSignal

class WorkerThread(QThread):
    log_signal = pyqtSignal(str)  # Tín hiệu để gửi log về giao diện chính

    def __init__(self, keywords, site, start_year, end_year, min_delay, max_delay, output_dir, output_file, page_limit):
        super().__init__()
        self.keywords = keywords
        self.site = site
        self.start_year = start_year
        self.end_year = end_year
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.output_dir = output_dir
        self.output_file = output_file
        self.page_limit = page_limit

    def run(self):
        # Chạy hàm extract_google_results trong thread riêng biệt
        extract_google_results(
            keywords=self.keywords,
            site=self.site,
            start_year=self.start_year,
            end_year=self.end_year,
            min_delay=self.min_delay,
            max_delay=self.max_delay,
            output_dir=self.output_dir,
            output_file=self.output_file,
            page_limit=self.page_limit,
            log_callback=self.emit_log  # Sử dụng emit_log để gửi tín hiệu
        )

    def emit_log(self, message):
        self.log_signal.emit(message)  # Gửi tín hiệu chứa log về giao diện chính


class SearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_config()  # Load config khi khởi động

    def initUI(self):
        # Tạo các thành phần giao diện
        self.keyword_label = QLabel('Danh sách từ khóa (mỗi từ khóa trên một dòng):')
        self.keyword_input = QTextEdit(self)
        self.keyword_input.setPlaceholderText("Nhập một từ khóa trên mỗi dòng")

        self.site_label = QLabel('Trang web:')
        self.site_input = QLineEdit(self)

        self.start_year_label = QLabel('Năm bắt đầu:')
        self.start_year_input = QLineEdit(self)

        self.end_year_label = QLabel('Năm kết thúc:')
        self.end_year_input = QLineEdit(self)

        self.min_delay_label = QLabel('Thời gian chờ tối thiểu:')
        self.min_delay_input = QLineEdit(self)

        self.max_delay_label = QLabel('Thời gian chờ tối đa:')
        self.max_delay_input = QLineEdit(self)

        self.page_limit_label = QLabel('Số trang cần tìm:')
        self.page_limit_input = QLineEdit(self)

        self.dir_label = QLabel('Thư mục lưu:')
        self.dir_input = QLineEdit(self)
        self.dir_button = QPushButton('Chọn thư mục', self)
        self.dir_button.clicked.connect(self.choose_directory)

        self.output_label = QLabel('Kết quả:')
        self.output_text = QTextEdit(self)  # Thay QLabel bằng QTextEdit để hiển thị thông tin
        self.output_text.setReadOnly(True)  # Chỉ đọc, không cho phép chỉnh sửa

        self.submit_button = QPushButton('Chạy tìm kiếm', self)
        self.submit_button.clicked.connect(self.run_search)

        # Bố trí các thành phần
        layout = QVBoxLayout()
        layout.addWidget(self.keyword_label)
        layout.addWidget(self.keyword_input)
        layout.addWidget(self.site_label)
        layout.addWidget(self.site_input)
        layout.addWidget(self.start_year_label)
        layout.addWidget(self.start_year_input)
        layout.addWidget(self.end_year_label)
        layout.addWidget(self.end_year_input)
        layout.addWidget(self.min_delay_label)
        layout.addWidget(self.min_delay_input)
        layout.addWidget(self.max_delay_label)
        layout.addWidget(self.max_delay_input)
        layout.addWidget(self.page_limit_label)
        layout.addWidget(self.page_limit_input)
        layout.addWidget(self.dir_label)
        layout.addWidget(self.dir_input)
        layout.addWidget(self.dir_button)
        layout.addWidget(self.output_label)
        layout.addWidget(self.output_text)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        self.setWindowTitle('Công cụ tìm kiếm Google')
        self.show()

    def choose_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu")
        if directory:
            self.dir_input.setText(directory)

    def run_search(self):
        keywords_text = self.keyword_input.toPlainText()
        keywords = [keyword.strip() for keyword in keywords_text.split('\n') if keyword.strip()]

        site = self.site_input.text()
        start_year = self.start_year_input.text()
        end_year = self.end_year_input.text()
        min_delay = self.min_delay_input.text()
        max_delay = self.max_delay_input.text()
        page_limit = self.page_limit_input.text()
        output_dir = self.dir_input.text()
        output_file = "results.csv"

        try:
            start_year = int(start_year)
            end_year = int(end_year)
            min_delay = float(min_delay)
            max_delay = float(max_delay)
            page_limit = int(page_limit)
        except ValueError as e:
            self.output_text.append(f"Lỗi: {e}. Vui lòng kiểm tra lại các giá trị nhập vào.")
            return

        self.save_config({
            'keyword': keywords_text,
            'site': site,
            'start_year': start_year,
            'end_year': end_year,
            'min_delay': min_delay,
            'max_delay': max_delay,
            'page_limit': page_limit,
            'output_dir': output_dir
        })

        self.output_text.append(f"Từ khóa: {', '.join(keywords)}")
        self.output_text.append(f"Trang web: {site}")
        self.output_text.append(f"Năm bắt đầu: {start_year}")
        self.output_text.append(f"Năm kết thúc: {end_year}")
        self.output_text.append(f"Thời gian chờ tối thiểu: {min_delay}")
        self.output_text.append(f"Thời gian chờ tối đa: {max_delay}")
        self.output_text.append(f"Số trang cần tìm: {page_limit}")
        self.output_text.append(f"Thư mục lưu: {output_dir}")

        # Khởi tạo WorkerThread
        self.worker = WorkerThread(
            keywords=keywords,
            site=site,
            start_year=start_year,
            end_year=end_year,
            min_delay=min_delay,
            max_delay=max_delay,
            output_dir=output_dir,
            output_file=output_file,
            page_limit=page_limit
        )

        # Kết nối tín hiệu từ WorkerThread với QTextEdit
        self.worker.log_signal.connect(self.output_text.append)
        self.worker.start()  # Bắt đầu thread

    def load_config(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.keyword_input.setPlainText(config.get('keyword', ''))  # Sử dụng setPlainText cho QTextEdit
                self.site_input.setText(config.get('site', ''))
                self.start_year_input.setText(str(config.get('start_year', '')))
                self.end_year_input.setText(str(config.get('end_year', '')))
                self.min_delay_input.setText(str(config.get('min_delay', '')))
                self.max_delay_input.setText(str(config.get('max_delay', '')))
                self.page_limit_input.setText(str(config.get('page_limit', '')))
                self.dir_input.setText(config.get('output_dir', ''))
        except FileNotFoundError:
            pass  # Nếu tệp cấu hình không tồn tại, không làm gì cả

    def save_config(self, config):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SearchApp()
    sys.exit(app.exec_())
