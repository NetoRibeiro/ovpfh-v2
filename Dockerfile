# Stage 1: Build and Generate Static Pages
FROM python:3.13-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright and Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (chromium)
RUN playwright install chromium

# Copy project files
COPY . .

# Run static site generation scripts
# We run match pages and team pages generation to ensure the site is fully populated
RUN python spiders/generate_match_pages.py || true
RUN python spiders/generate_team_pages.py || true

# Stage 2: Final image - Serve with Nginx
FROM nginx:alpine

# Copy the generated site from the builder stage
COPY --from=builder /app /usr/share/nginx/html

# Copy custom Nginx configuration
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
