FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Start with Vite preview
EXPOSE 80
CMD ["sh", "-c", "npm run start"]
