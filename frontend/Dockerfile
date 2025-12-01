# frontend/Dockerfile
FROM node:20-alpine

# Set working dir
WORKDIR /app

# Install deps
COPY package*.json ./
RUN npm install

# Copy rest of the frontend code
COPY . .

# Expose React dev server port
EXPOSE 3000

# Start React app
CMD ["npm", "start"]
