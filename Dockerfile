# Specify base image
FROM debian:bookworm-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install required system packages
## Clean up cache to reduce image size
RUN apt-get update && apt-get -y install \
    curl \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && curl -sSL "https://caddyserver.com/api/download?os=linux&arch=amd64" -o /usr/bin/caddy \
    && chmod +x /usr/bin/caddy \
    && rm -rf /var/lib/apt/lists/*

# Optimize Python execution inside the container
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_INSTALL_DIR=/usr/local

ENV NODE_OPTIONS="--max-old-space-size=256"

WORKDIR /lemonade-stand

# Install dependencies without installing the project itself
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-cache

# Copy the processed Parquet data to root directory - To skip data processing hence avoid OOM issues
COPY tests/_mocks/.lemonade-stand /root/.lemonade-stand
COPY . .

ARG REFLEX_API_URL

# Initialize Reflex and pre-compile the frontend
RUN uv run reflex init
RUN REFLEX_API_URL=$REFLEX_API_URL uv run reflex export --frontend-only --loglevel debug \
    && unzip frontend.zip -d public \
    && rm frontend.zip

EXPOSE 8080

# Start Caddy in the background, then Reflex in production mode
CMD ["sh", "-c", "caddy start --config Caddyfile && unset PORT && uv run reflex run --env prod --backend-only"]
