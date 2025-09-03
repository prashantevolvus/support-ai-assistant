FROM python:3.9-slim
WORKDIR /app
# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy application source
COPY . .
# Expose the API port and run the server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]