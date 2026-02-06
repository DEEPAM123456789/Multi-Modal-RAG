FROM python:3.10-slim

WORKDIR /app

# System deps for PDF + OCR + OpenCV
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libgl1 \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# ---------- PIP CACHE LAYER (VERY IMPORTANT) ----------
# Copy only requirements first so Docker can cache torch install
COPY requirements.txt .

RUN pip install --upgrade pip

# Create a pip cache directory inside image (persist between builds)
RUN pip install --no-cache-dir --upgrade wheel setuptools

# Install heavy ML deps first (they rarely change)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining requirements
RUN pip install --no-cache-dir -r requirements.txt
# ------------------------------------------------------

# Now copy project code (this changes often)
COPY frontend ./frontend
COPY backend ./backend
COPY entrypoint.sh .

# Convert line endings and make executable
RUN dos2unix entrypoint.sh && chmod +x entrypoint.sh

# Create directory for persistent storage (or ephemeral on Render)
# and set permissions so any user can write to it
RUN mkdir -p dbv2/chroma_db && chmod -R 777 dbv2

ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_HEADLESS=true

EXPOSE 8000
EXPOSE 8501

CMD ["./entrypoint.sh"]
