import os
import requests
from git import Repo
from transformers import AutoTokenizer, AutoModel
from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams
import torch

from clearml import Task
task = Task.init(project_name='ETL Pipeline Project', task_name='Featurization Pipeline', task_type=Task.TaskTypes.optimizer)

client = MongoClient("mongodb://localhost:27017/")
db = client["media_database"]
documentation_collection = db["documentation"]
video_collection = db["youtube_video"]

qdrant = QdrantClient("localhost", port=6333)

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

def featurize_text(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embeddings

def process_documentation_files():
    documentation_files = [file for file in os.listdir("ros2_docs") if file.endswith(".md") or file.endswith(".html")]
    for file in documentation_files:
        with open(os.path.join("ros2_docs", file), 'r', encoding="utf-8") as f:
            text = f.read()
            embedding = featurize_text(text)
            documentation_collection.insert_one({"file_name": file, "embedding": embedding.tolist()})
            qdrant.upsert(
                collection_name="documentation",
                points=[{
                    'id': file,
                    'vector': embedding.tolist()
                }]
            )

def process_video_urls():
    video_urls = ["https://www.youtube.com/watch?v=some_video_id"]
    for url in video_urls:
        video_info = download_video_info(url)
        video_description = video_info.get('description', '')
        embedding = featurize_text(video_description)
        video_collection.insert_one({"url": url, "embedding": embedding.tolist()})
        qdrant.upsert(
            collection_name="youtube_video",
            points=[{
                'id': url,
                'vector': embedding.tolist()
            }]
        )

def download_video_info(url):
    import yt_dlp
    with yt_dlp.YoutubeDL() as ydl:
        result = ydl.extract_info(url, download=False)
    return result

process_documentation_files()
process_video_urls()

print("Featurization completed and data inserted into MongoDB and Qdrant.")

