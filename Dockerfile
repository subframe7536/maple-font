FROM python:3.11-slim

# Install system dependencies including FontForge
RUN apt-get update \
    && apt-get install -y fontforge \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements.txt first to avoid duplication installation
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the project files
COPY . .

# Create volume mount points
VOLUME /app/fonts

# Default build arguments
ENV BUILD_ARGS=""

# Run the build script with optional arguments
ENTRYPOINT ["sh", "-c", "python build.py $BUILD_ARGS"]
