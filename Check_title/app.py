import streamlit as st
import csv
import re
import os

st.set_page_config(layout="wide")
st.title("Hiển thị nội dung bài báo và phân tích")

# Đường dẫn file
csv_file = os.path.join(os.path.dirname(__file__), "all_articles.csv")
output_file = os.path.join(os.path.dirname(__file__), "output.txt")

# Đọc dữ liệu từ file CSV
articles = {}
with open(csv_file, 'r', encoding='utf-8') as csv_f:
    csv_reader = csv.DictReader(csv_f)
    for row in csv_reader:
        articles[row['title']] = row['content']

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

col1, col2 = st.columns(2)
article_titles = list(articles.keys())
selected_title = st.selectbox("Chọn bài báo", article_titles)

with col1:
    st.subheader("Nội dung bài báo")
    st.write(articles[selected_title])

with col2:
    st.subheader("Phân tích từ Gemini")
    if selected_title in analyses:
        st.write(analyses[selected_title])
    else:
        st.write("Chưa có phân tích cho bài báo này.")

if st.button("Tải lại dữ liệu"):
    st.experimental_rerun()