# Stage 1: Build and Generate Static Pages
FROM python:3.13-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Run static site generation scripts
# We run match pages and team pages generation to ensure the site is fully populated
# We remove || true to ensure the build fails if the generation fails (easier to debug)
RUN python spiders/generate_match_pages.py
RUN python spiders/generate_team_pages.py

# Stage 2: Final image - Serve with Nginx
FROM nginx:alpine

# Copy the generated site from the builder stage
COPY --from=builder /app /usr/share/nginx/html

# Copy custom Nginx configuration
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/default.conf

# Copy environment injection script (replaces placeholders in firebase-config.js at runtime)
COPY --from=builder /app/js/inject-env.sh /docker-entrypoint.d/01-inject-env.sh
RUN chmod +x /docker-entrypoint.d/01-inject-env.sh

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
