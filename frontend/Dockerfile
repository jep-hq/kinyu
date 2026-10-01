# Frontend Dockerfile
FROM node:20-slim AS base
# Set up pnpm
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app

# Build stage
FROM base AS build
COPY package.json pnpm-lock.yaml* ./
# Remove frozen-lockfile to allow bootstrap without lockfile
RUN pnpm install
COPY . .
RUN pnpm run build

# Production stage
FROM base AS production
COPY --from=build /app/.output /app/.output
# Nuxt output is standalone
CMD ["node", ".output/server/index.mjs"]
