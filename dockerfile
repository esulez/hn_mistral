FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy workflow code
COPY workflow.py .

# Set environment variables (will be overridden by deployment)
ENV MISTRAL_API_KEY=""

# Command to run the worker
CMD ["python", "-m", "mistralai.workflows.worker", "--workflow", "workflow.HackerNewsTechDigestWorkflow"]