#!/bin/bash
# This script installs Node.js and scaffolds a new React app on Ubuntu (WSL)

# Update package index and install prerequisites
sudo apt-get update && sudo apt-get install -y curl

# Install Node.js (version 18.x is used as an example; you can adjust if needed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
echo "Node.js version:" $(node -v)
echo "npm version:" $(npm -v)

# Create a new React app using create-react-app via npx (best practice: no global install)
APP_NAME="skyDaddy"
npx create-react-app $APP_NAME

echo "React app '$APP_NAME' has been created successfully."
echo "To start the app, navigate to the directory and run 'npm start'."
