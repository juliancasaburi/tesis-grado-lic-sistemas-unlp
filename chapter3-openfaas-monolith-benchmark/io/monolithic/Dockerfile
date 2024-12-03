# Use the official Node.js 20 Alpine image as the base image
FROM node:20-alpine3.19

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory for dependency installation
COPY package*.json ./

# Install the app dependencies
RUN npm install

# Install pm2 globally
RUN npm install pm2 -g

# Copy the main application file and PM2 ecosystem config
COPY server.js ./
COPY ecosystem.config.js ./

# Expose the port on which the app will run
EXPOSE 3000

# Start the app using pm2
CMD ["pm2-runtime", "start", "ecosystem.config.js"]
