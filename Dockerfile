FROM python:3.8.12-buster

WORKDIR /backend

COPY . /backend/

RUN pip install -r requirements.txt

RUN cat util.txt > ../usr/local/lib/python3.8/site-packages/object_detection/utils/label_map_util.py

EXPOSE 8000


CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]