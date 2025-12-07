FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy dependency list first and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then copy the rest of the source code
COPY . .

# Start FastAPI (Cloud Run injects the PORT environment variable)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
