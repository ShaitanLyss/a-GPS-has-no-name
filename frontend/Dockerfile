# Stage 1: Build the app
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
FROM node:21-bookworm-slim

WORKDIR /app

# Copy the built app from the previous stage
COPY --from=builder /app/build /app/package*.json ./

# Install only production dependencies using pnpm
RUN npm install -g pnpm
RUN pnpm install --prod

# Expose the port
EXPOSE 3000

# Start the app
CMD ["node", "."]

