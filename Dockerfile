# syntax=docker/dockerfile:1

FROM python:3.7-windowsservercore-1809 

WORKDIR /user/src/File Watcher

COPY requirements.txt ./ 
RUN pip install -r requirements.txt
COPY . .

ENTRYPOINT ["python", "./file_watcher.py"] 