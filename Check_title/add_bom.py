import os

def add_bom_to_csv(file_path):
    # Đọc nội dung từ tệp CSV hiện tại
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Thêm ký tự BOM vào đầu tệp và ghi nội dung vào tệp mới
    with open(file_path, 'w', encoding='utf-8-sig') as file:
        file.write(content)

# Đường dẫn đến tệp CSV hiện tại
csv_file_path = r"D:\Project\Crawl_Data\Check_title\can_tho.csv"


# Kiểm tra xem tệp có tồn tại không
if os.path.exists(csv_file_path):
    add_bom_to_csv(csv_file_path)
    print(f"Added BOM to {csv_file_path}")
else:
    print(f"File {csv_file_path} does not exist.")
