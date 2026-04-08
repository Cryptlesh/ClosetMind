# Step 1: Build Phase
FROM node:20-slim AS build-stage

WORKDIR /app

# Accept Build Argument for API Base URL
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code and build
COPY . .
RUN npm run build

# Step 2: Production Phase
FROM nginx:stable-alpine

# Copy built assets from build-stage to nginx public directory
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy custom nginx config if needed (optional)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
