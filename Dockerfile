# ─────────────────────────────────────────────────────────────────────────────
# Resource Link Hub - Backend Dockerfile
# Base: python:3.11-slim | Port: 5000
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create the persistent data directory
RUN mkdir -p /var/lib/backend_data

# Copy application source
COPY app.py .

# Expose the API port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]

