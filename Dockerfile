FROM python:3.10

WORKDIR /app

# System deps for PDF + OCR + OpenCV
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements first (layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    --default-timeout=1000 \
    --retries 10 \
    -r requirements.txt

# Copy app code
COPY frontend ./frontend
COPY backend ./backend
COPY entrypoint.sh .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_HEADLESS=true

EXPOSE 8000
EXPOSE 8501

CMD ["./entrypoint.sh"]
