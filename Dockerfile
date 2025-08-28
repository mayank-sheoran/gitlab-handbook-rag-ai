FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Expose ports for backend and frontend
EXPOSE 9999
EXPOSE 9998

