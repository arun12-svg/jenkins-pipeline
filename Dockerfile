FROM python:3.11-slim

WORKDIR /app

# Copy all project files
COPY . .

# Install Flask (lightweight server for demonstration)
RUN pip install flask

# Create a simple app if none exists
RUN cat << 'EOF' > app.py
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Your Jenkins Pipeline Deployment is Working!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
EOF

EXPOSE 8080

CMD ["python3", "app.py"]
