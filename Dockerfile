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

# Create a clean config that handles React routing and port binding
RUN echo 'server { \
    listen       8080; \
    server_name  localhost; \
    location / { \
        root   /usr/share/nginx/html; \
        index  index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 8080

# At runtime, replace the hardcoded 8080 with the actual $PORT provided by Cloud Run
CMD ["/bin/sh", "-c", "sed -i 's/8080/'${PORT:-8080}'/g' /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
