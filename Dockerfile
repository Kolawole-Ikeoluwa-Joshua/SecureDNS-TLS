# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# # Update package lists, install tls packages, and clean up to minimize image size 
RUN apt-get update && \
    apt-get install -y --no-install-recommends openssl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Make port 53 available to the world outside this container
EXPOSE 53/udp 53/tcp

# Define environment variable
ENV NAME DNSoverTLSProxy

# Run proxy.py when the container launches
CMD ["python3", "proxy.py"]
