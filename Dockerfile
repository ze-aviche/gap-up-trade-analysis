# Use a lightweight Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy the application code into the container
COPY main.py .

# Define the command to run the script when the container starts
CMD ["python", "main.py"]