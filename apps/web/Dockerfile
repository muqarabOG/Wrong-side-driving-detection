# Step 1: Build the React app
FROM node:18-alpine as build-stage

WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application
COPY . .

# Build for production
RUN npm run build

# Step 2: Serve the build using Nginx
FROM nginx:stable-alpine as production-stage

# Copy the build output to nginx folder
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy custom nginx config if needed (optional)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
