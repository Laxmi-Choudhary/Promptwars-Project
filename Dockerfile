FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port and run Streamlit
EXPOSE 8080
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
