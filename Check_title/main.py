import torch
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoModel, AutoTokenizer
from tqdm import tqdm

# Tải PhoBERT model & tokenizer
MODEL_NAME = "vinai/phobert-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)
phobert_model = AutoModel.from_pretrained(MODEL_NAME)

# Hàm lấy embedding từ PhoBERT
def get_embedding(text):
    tokens = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=256)
    with torch.no_grad():
        output = phobert_model(**tokens)
    embedding = output.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embedding

# Danh sách nhãn chủ đề
labels = [
    "biến đổi khí hậu", "khủng hoảng khí hậu", "tác động khí hậu", "hiệu ứng nhà kính",
    "khí nhà kính", "phát thải", "khí hậu cực đoan", "nhiệt độ toàn cầu",
    "khí thải công nghiệp", "mực nước biển dâng", "băng tan", "lũ lụt", "hạn hán",
    "suy thoái môi trường", "mất đa dạng sinh học", "năng lượng tái tạo", "bảo vệ rừng",
    "giảm phát thải", "phát triển bền vững", "thảm họa khí hậu", "thiên tai cực đoan",
    "metan", "ngày Trái đất", "giờ Trái đất", "công nghệ xanh", "rừng ngập",
    "ô nhiễm khí hậu", "sóng nhiệt", "mưa acid", "khí hậu", "biến đổi", "phát thải",
    "môi trường", "nhà kính", "băng", "rừng", "năng lượng", "thảm họa", "thiên tai",
    "CO2", "chính sách khí hậu", "hiệp định Paris", "COP26", "COP27", "COP28",
    "COP29", "IPCC", "hành động khí hậu", "chiến lược khí hậu", "liên hợp quốc",
    "phát triển xanh", "quốc tế về khí hậu", "chính sách của Đảng",
    "chiến lược phát triển bền vững", "phát thải ròng", "thích ứng",
    "ứng phó", "nước biển dâng", "tín chỉ carbon", "COP"]

# Tạo embedding cho nhãn chủ đề
label_embeddings = {label: get_embedding(label) for label in labels}

# Danh sách các file cần xử lý
file_paths = [
    (r"D:\Project\Crawl_Data\Ca Mau.csv", r"D:\Project\Crawl_Data\Ca Mau_with_relevance.csv"),
    (r"D:\Project\Crawl_Data\Can Tho.csv", r"D:\Project\Crawl_Data\Can Tho_with_relevance.csv"),
    (r"D:\Project\Crawl_Data\Hau Giang.csv", r"D:\Project\Crawl_Data\Hau Giang_with_relevance.csv")
]

# Xử lý từng file riêng biệt
for input_path, output_path in file_paths:
    print(f"\nĐang xử lý file: {input_path}")

    # Đọc file CSV
    df = pd.read_csv(input_path)
    df = df.drop_duplicates(subset=['Title'])

    # Phân loại từng tiêu đề trong CSV
    relevance_scores = []
    for title in tqdm(df['Title']):
        title_emb = get_embedding(title)
        similarities = {
            label: cosine_similarity([title_emb], [label_embeddings[label]])[0][0]
            for label in labels
        }

        # Xác định nhãn có độ tương đồng cao nhất
        best_label = max(similarities, key=similarities.get)
        best_score = similarities[best_label]
        relevance_scores.append(f"{best_score:.4f}")

    # Thêm cột "RelevanceScore" vào DataFrame
    df["RelevanceScore"] = relevance_scores

    # Lưu kết quả vào file CSV mới
    df.to_csv(output_path, index=False)

    # Thêm BOM cho file output
    with open(output_path, 'r', encoding='utf-8') as file:
        content = file.read()
    with open(output_path, 'w', encoding='utf-8-sig') as file:
        file.write(content)

    print(f"✔️ Đã lưu file: {output_path}")
