FROM node:22-alpine

# Install Git for version control support
RUN apk add --no-cache git

# Install the Gemini CLI
RUN npm install -g @google/gemini-cli

# Set up directories
RUN mkdir -p /gemini /workspace

# Set working directory
WORKDIR /workspace

# Default command - start gemini in interactive agent mode
CMD ["gemini"]
