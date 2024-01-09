FROM ubuntu:22.04
RUN apt-get update -y && apt-get install python3-pip python-is-python3 tesseract-ocr -y
WORKDIR /app
COPY ./req.txt /app/req.txt
RUN pip install -r req.txt
COPY . /app

CMD ["python3", "./main.py"]
