# Stage 1: Build & Dependencies
FROM node:20-alpine AS builder

WORKDIR /usr/src/app

# Security: Install dependencies with package locks and clean cache
COPY application/package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy application sources
COPY application/src ./src

# Stage 2: Minimal Distroless / Hardened Alpine Runtime
FROM node:20-alpine AS runner

# Security hardening: Create non-privileged user and group
RUN addgroup -g 10001 devopsgroup && \
    adduser -u 10001 -G devopsgroup -s /bin/sh -D devopsuser && \
    mkdir -p /data && chown -R devopsuser:devopsgroup /data

WORKDIR /app

# Copy production artifacts from builder
COPY --from=builder --chown=devopsuser:devopsgroup /usr/src/app/node_modules ./node_modules
COPY --from=builder --chown=devopsuser:devopsgroup /usr/src/app/src ./src
COPY --from=builder --chown=devopsuser:devopsgroup /usr/src/app/package.json ./package.json

# Environment parameters
ENV PORT=8080 \
    NODE_ENV=production \
    APP_ENV=production \
    DATA_STORAGE_PATH=/data/portal-data.log

# Switch to non-root user
USER devopsuser:devopsgroup

# Healthcheck configuration
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8080/healthz || exit 1

EXPOSE 8080

CMD ["node", "src/server.js"]
