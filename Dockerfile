# Use an official Python runtime as a parent image
FROM python:3.9-slim

RUN apt-get update && apt-get install -y sqlite3


RUN mkdir /app

# Set the working directory in the container
WORKDIR /app

#Copy Everything
COPY . .

# Copy the requirements file into the working directory
#COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the working directory
#COPY app.py .
#COPY templates/ templates/

# Expose the port the app runs on
EXPOSE 5000

# Run the application using Gunicorn
#CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]