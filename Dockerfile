# Specify base image
FROM debian:bookworm-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install required system packages
## Clean up cache to reduce image size
RUN apt-get update && apt-get -y install \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Optimize Python execution inside the container
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /lemonade-stand

# Install dependencies without installing the project itself
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-cache

# Copy application source code
COPY . .

# Expose frontend and backend ports
EXPOSE 3000
EXPOSE 8000

CMD ["uv", "run", "reflex", "run"]
