import os
import requests
from git import Repo
import yt_dlp
from pymongo import MongoClient
from clearml import Task

task = Task.init(project_name='ETL Pipeline Project', task_name='ETL Pipeline', task_type=Task.TaskTypes.optimizer)

repo_url = "https://github.com/ros2/ros2_documentation"
repo_dir = "ros2_docs"

if not os.path.exists(repo_dir):
    Repo.clone_from(repo_url, repo_dir)
else:
    repo = Repo(repo_dir)
    repo.remotes.origin.pull()

documentation_files = [os.path.join(repo_dir, file) for file in os.listdir(repo_dir) if file.endswith('.md') or file.endswith('.html')]

youtube_urls = ["https://www.youtube.com/watch?v=some_video_id"]

def download_video_info(url):
    with yt_dlp.YoutubeDL() as ydl:
        result = ydl.extract_info(url, download=False)
        return result['url']

video_urls = [download_video_info(url) for url in youtube_urls]

client = MongoClient("mongodb://localhost:27017/")
db = client["media_database"]
collection = db["ingested_urls"]

for doc in documentation_files:
    collection.insert_one({"url": doc, "type": "documentation"})

for video_url in video_urls:
    collection.insert_one({"url": video_url, "type": "youtube_video"})

urls = collection.find()
print("Ingested URLs:")
for url in urls:
    print(url["url"])

