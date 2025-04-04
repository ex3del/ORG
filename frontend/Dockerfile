FROM node:20-slim

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Create production build
RUN npm run build

# Install serve to run the production build
RUN npm install -g serve

EXPOSE 3000

# Run the app using serve with SPA flag
CMD ["serve", "-s", "build", "-l", "3000", "--single"]