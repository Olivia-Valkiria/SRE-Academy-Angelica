# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Expose Flask port
EXPOSE 5000

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set Flask environment variables
ENV FLASK_APP_FILE="app.py"
ENV FLASK_ENV=production

# Run the app (manual instrumentation already in app.py)
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

#--- IGNORE ---
# Note: OpenTelemetry auto-instrumentation is not used here since manual instrumentation is implemented in app.py
# If you want to use auto-instrumentation instead, uncomment the following lines and adjust app.py accordingly
# ENV OTEL_PYTHON_AUTO_INSTRUMENTATION_ENABLED=true
# CMD ["opentelemetry-instrument", "flask", "run", "--host=
