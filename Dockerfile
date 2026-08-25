FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# ============================================================
# Local Docker Compose Version
# ============================================================
# CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]


# ============================================================
# Render Version
# ============================================================
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]