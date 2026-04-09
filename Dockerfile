FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Copy requirements dan install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium
# Copy semua file
COPY . .

# Expose port (FastAPI default 8000)
EXPOSE 8000

CMD ["python", "main.py"]