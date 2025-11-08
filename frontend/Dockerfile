# Frontend Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# Build arguments for Vite environment variables
ARG VITE_API_URL=http://localhost:8000
ARG VITE_WS_URL=ws://localhost:8000

# Copy package files
COPY package.json bun.lock* yarn.lock* package-lock.json* ./

# Install dependencies
RUN if [ -f bun.lock ]; then \
      npm install -g bun && bun install; \
    elif [ -f yarn.lock ]; then \
      yarn install --frozen-lockfile; \
    else \
      npm ci; \
    fi

# Copy frontend source
COPY . .

# Set environment variables for build
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_WS_URL=$VITE_WS_URL

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Install serve for preview and curl for healthchecks
RUN npm install -g serve && \
    apk add --no-cache curl

# Copy built files from builder
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 4173

# Run preview server
CMD ["serve", "-s", "dist", "-l", "4173"]

