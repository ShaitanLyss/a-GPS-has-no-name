
# Stage 1: Build the app
FROM node:21-bookworm-slim as prod_deps
RUN npm install -g pnpm
COPY app/package*.json app/pnpm-lock.yaml ./
RUN pnpm install --prod

FROM node:21-bookworm-slim AS builder

WORKDIR /app

# Copy package.json and package-lock.json
COPY app/package*.json ./

# Install dependencies using pnpm
RUN npm install -g pnpm
RUN pnpm install


# Copy the rest of the app's source code
COPY app/. .

# Build the app
RUN pnpm build

# Stage 2: Create the production image
FROM prod_deps AS production
WORKDIR /app

# Copy the built app from the previous stage
COPY --from=builder /app/build ./
COPY app/package.json .

# Expose the port
EXPOSE 3000

# Start the app
ENTRYPOINT [ "node","index.js" ]

