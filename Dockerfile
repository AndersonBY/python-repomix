FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
RUN mkdir /repomix
WORKDIR /repomix

# Copy project files
COPY . .

# Install PDM and dependencies, then build and install the package
# To reduce the size of the layer, these commands are executed in the same RUN command
RUN pip install --no-cache-dir pdm \
    && pdm install --prod \
    && pdm build \
    && pip install dist/*.whl \
    && pip uninstall -y pdm \
    && rm -rf /root/.cache/pip \
    && rm -rf /root/.cache/pdm

# Set working directory for user code
WORKDIR /app

# Verify installation
RUN repomix --version
RUN repomix --help

ENTRYPOINT ["repomix"]