# Start from a lightweight Python base
FROM python:3.12-slim

ENV DOCKER_MODE true

# Set the working directory
WORKDIR /yafa

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into the container
COPY . .

CMD ["python", "-u", "./yafa/main.py"]
