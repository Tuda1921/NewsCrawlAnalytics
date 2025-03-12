import streamlit as st
import csv
import re

# Thiết lập cấu hình trang
st.set_page_config(layout="wide")
st.title("Hiển thị nội dung bài báo và phân tích")

# Thêm CSS để bật wrap
st.markdown("""
    <style>
    .wrap-text {
        white-space: normal;
        word-wrap: break-word;
    }
    </style>
""", unsafe_allow_html=True)

# Tên file
csv_file = "all_articles.csv"
output_file = "output.txt"

# Đọc dữ liệu từ file CSV
articles = {}
with open(csv_file, 'r', encoding='utf-8') as csv_f:
    csv_reader = csv.DictReader(csv_f)
    for row in csv_reader:
        articles[row['title']] = row['content']

# Dropdown để chọn bài báo
article_titles = list(articles.keys())
selected_title = st.selectbox("Chọn bài báo", article_titles)

# Đọc dữ liệu từ file output.txt
analyses = {}
current_title = None
current_analysis = []

with open(output_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        match = re.match(r"=== Bài báo: (.+) ===", line.strip())
        if match:
            if current_title and current_analysis:
                analyses[current_title] = "\n".join(current_analysis)
            current_title = match.group(1)
            current_analysis = []
        elif line.strip() == "====================":
            if current_title and current_analysis:
                analyses[current_title] = "\n".join(current_analysis)
            current_title = None
            current_analysis = []
        elif current_title:
            current_analysis.append(line.strip())

# Tạo giao diện với hai cột
col1, col2 = st.columns(2)

# Hiển thị nội dung bài báo ở cột 1 với wrap và màu
with col1:
    st.subheader("Nội dung bài báo")
    st.write(articles[selected_title], unsafe_allow_html=False, key="content", css_class="wrap-text")

# Hiển thị phân tích ở cột 2 với wrap và màu
with col2:
    st.subheader("Phân tích")
    if selected_title in analyses:
        st.write(analyses[selected_title], unsafe_allow_html=False, key="analysis", css_class="wrap-text")
    else:
        st.write("Chưa có phân tích cho bài báo này.")
