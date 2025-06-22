# Use a specific, stable Python version as the parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker's layer caching
COPY requirements.txt .

# Install dependencies
# --no-cache-dir reduces image size. --trusted-host is for potential network issues inside build envs.
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the application's code from your host to the image filesystem.
# This includes main.py, the agents/ folder, data/, etc.
COPY . .

# Expose the port that Streamlit runs on to the outside world
EXPOSE 8080

# Define the command to run your app when the container starts.
# We use the robust python -m streamlit run command.
# --server.headless=true is best practice for cloud deployments.
CMD ["streamlit", "run", "main.py", "--server.port=8080", "--server.address=0.0.0.0"]