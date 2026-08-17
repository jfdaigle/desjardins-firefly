FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir pdfplumber

COPY parser.py .

CMD ["python", "parser.py"]
