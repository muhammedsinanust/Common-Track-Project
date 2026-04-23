FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the React app with direct service URLs baked in
ENV REACT_APP_AUTH_SERVICE_URL=http://localhost:8001
ENV REACT_APP_PRODUCT_SERVICE_URL=http://localhost:8002
ENV REACT_APP_RAFFLE_SERVICE_URL=http://localhost:8003
RUN npm run build

# Production stage - serve with nginx
FROM nginx:alpine

# Copy nginx config — serve on port 3000, no proxy to gateway
RUN echo 'server { \
  listen 3000; \
  location / { \
    root /usr/share/nginx/html; \
    index index.html; \
    try_files $uri $uri/ /index.html; \
  } \
}' > /etc/nginx/conf.d/default.conf

# Copy built app from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
