FROM node:22-slim

# Install the Gemini CLI
RUN npm install -g @google/gemini-cli

# Set up a workspace directory
WORKDIR /app

# Default command to run gemini CLI
ENTRYPOINT ["gemini"]
