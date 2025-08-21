#!/bin/bash
set -e

echo "🚀 SIMPLE DEPLOYMENT APPROACH"

# Build locally first
echo "Building locally..."
npm install --legacy-peer-deps
npm run build

# Create a simple static deployment
echo "Creating simple static deployment..."

# Copy built files to a simple structure
mkdir -p simple_deploy
cp -r dist/* simple_deploy/

# Create a simple Dockerfile for static serving
cat > simple_deploy/Dockerfile << 'DOCKERFILE'
FROM nginx:alpine
COPY . /usr/share/nginx/html
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
DOCKERFILE

# Create nginx config
cat > simple_deploy/nginx.conf << 'NGINX'
server {
    listen 8080;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /healthz {
        return 200 '{"status":"ok"}';
        add_header Content-Type application/json;
    }
}
NGINX

echo "✅ Simple deployment ready in simple_deploy/"
ls -la simple_deploy/
