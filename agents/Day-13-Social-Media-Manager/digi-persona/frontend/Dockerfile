FROM node:20-slim

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package.json and pnpm-lock.yaml
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install

# Copy the rest of the application
COPY . .

# Skip build step for development
# RUN pnpm build

# Expose the port the app runs on
EXPOSE 5173

# Set environment variables
ENV DOCKER_ENV=true

# Command to run the app
CMD ["pnpm", "dev", "--host", "0.0.0.0"]
