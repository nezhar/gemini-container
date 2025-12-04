# Gemini Container

A containerized environment for running the Gemini CLI agent with optional API logging and visualization capabilities. Inspired by [nezhar/claude-container](https://github.com/nezhar/claude-container).

## Features

- 🤖 **Interactive agent mode** - Run Gemini as an interactive agent with the `gemini` command
- 🐳 **Fully containerized** Gemini CLI environment
- 🔐 **Persistent credentials** across sessions
- 📊 **Optional API logging** with mitmproxy
- 📈 **Web interface** for analyzing API requests via Datasette
- 🛠️ **Multiple installation methods** (helper script, Docker Compose, or direct Docker)

## Quick Start

### Option 1: Helper Script (Recommended)

**Installation:**

Download and install the helper script:

```bash
curl -o ~/.local/bin/gemini-container https://raw.githubusercontent.com/nezhar/gemini-container/main/bin/gemini-container
chmod +x ~/.local/bin/gemini-container
```

Make sure `~/.local/bin` is in your PATH.

**First Time Setup:**

Run the script for the first time:

```bash
gemini-container
```

The script will:
1. Initialize credential templates in `~/.config/gemini-container/config/`
2. Prompt you to set up authentication
3. Start the Gemini agent

In the agent, run `/login` and follow the OAuth flow to authenticate.

**Usage Examples:**

```bash
# Start Gemini agent (interactive mode)
gemini-container

# With API logging enabled
gemini-container --proxy --datasette

# Using API key instead of OAuth
GEMINI_API_KEY=your-key gemini-container

# Using a specific workspace directory
gemini-container -w /path/to/project
```

### Option 2: Docker Compose

Clone this repository and run:

```bash
docker compose run --rm gemini-cli
```

### Option 3: Legacy run.sh Script

For backward compatibility:

```bash
./run.sh [gemini-cli arguments]
```

## Repository Structure

```
gemini-container/
├── bin/
│   └── gemini-container          # Helper script for easy usage
├── gemini-cli/
│   └── Dockerfile                # Main Gemini CLI container
├── gemini-proxy/
│   ├── Dockerfile                # Proxy container
│   ├── proxy.py                  # mitmproxy script
│   ├── start.sh                  # Proxy startup script
│   └── requirements.txt          # Python dependencies
├── gemini-datasette/
│   ├── Dockerfile                # Datasette container
│   └── requirements.txt          # Python dependencies
├── example/
│   └── compose.yml               # Example runtime configuration
├── compose.yml                   # Build configuration
└── README.md
```

## Configuration Directory Structure

After running gemini-container, your configuration will be organized as follows:

```
~/.config/gemini-container/
├── config/                       # Gemini CLI configuration
│   ├── google_accounts.json     # OAuth credentials
│   └── settings.json             # Gemini CLI settings
└── proxy/                        # Proxy data (when --proxy is used)
    ├── .mitmproxy/               # mitmproxy certificates
    │   └── mitmproxy-ca-cert.pem # Proxy CA certificate
    └── logs.db                   # API request logs (SQLite database)
```

This structure keeps different components isolated and makes it easy to add more components in the future.

## Prerequisites

### Docker

Ensure Docker is installed and running on your system.

### Authentication Setup

The helper script automatically initializes credential templates on first run. You have two options for authentication:

#### Option A: OAuth Credentials (Recommended)

**Automatic Setup (First Run):**

On the first run, `gemini-container` will:
1. Create `~/.config/gemini-container/config/` directory
2. Copy credential template files
3. Prompt you to authenticate

When the container starts, simply run:
```
/login
```

Then follow the OAuth authentication flow in your browser.

**Manual Setup (Optional):**

If you already have Gemini CLI credentials, you can copy them manually:

```bash
mkdir -p ~/.config/gemini-container/config
cp /path/to/your/google_accounts.json ~/.config/gemini-container/config/
cp /path/to/your/settings.json ~/.config/gemini-container/config/
```

**Note:** All credentials and container configuration are stored in `~/.config/gemini-container`. Make sure this directory stays in your `.gitignore` if you're working in a git repository.

#### Option B: API Key

Use the `GEMINI_API_KEY` environment variable:

```bash
GEMINI_API_KEY=your-api-key gemini-container
```

**Note:** API key authentication only provides access to the basic Flash model, not Pro models.

## Helper Script Usage

The `gemini-container` script provides a convenient interface for running the containerized Gemini CLI.

### Basic Commands

```bash
# Show help
gemini-container --help

# Start Gemini agent
gemini-container

# Specify a workspace directory
gemini-container -w /path/to/project

# Use custom config directory
gemini-container -c /path/to/custom/config
```

### API Logging

Enable the proxy to log all API requests to a SQLite database:

```bash
gemini-container --proxy
```

**Note:** On first run with `--proxy`, the script will:
1. Start the proxy container
2. Wait for the mitmproxy CA certificate to be generated (up to 30 seconds)
3. Mount the certificate into the Gemini container
4. Configure environment variables for SSL interception

Enable Datasette to visualize the logs in a web interface:

```bash
gemini-container --proxy --datasette
```

Access the Datasette interface at [http://localhost:8001/](http://localhost:8001/) to explore:
- Request/response details
- Token usage and costs
- Filter and sort by various criteria
- Export data for further analysis

### Container Management

```bash
# Stop the proxy
gemini-container --stop-proxy

# Stop Datasette
gemini-container --stop-datasette

# Clean up all containers and network
gemini-container --cleanup
```

## Building Images

The root `compose.yml` is used for building all three Docker images:

```bash
# Build all images
docker compose build

# Build with specific version tag
GEMINI_CONTAINER_VERSION=1.0.0 docker compose build

# Build individual image
docker compose build gemini-cli
docker compose build gemini-proxy
docker compose build gemini-datasette
```

## Docker Compose Usage (Advanced)

For runtime usage with Docker Compose, see the example configuration:

```bash
# Copy the example
cp example/compose.yml docker-compose.yml

# Run with all services (proxy + datasette)
docker compose up -d gemini-proxy gemini-datasette
docker compose run --rm gemini-cli

# Stop all services
docker compose down
```

### Environment Variables

Customize the setup with environment variables:

```bash
# Set custom version
GEMINI_CONTAINER_VERSION=1.0.0 docker compose build

# Set custom ports
PROXY_PORT=9090 DATASETTE_PORT=9001 docker compose up

# Use different workspace
WORKSPACE_DIR=/path/to/project docker compose run --rm gemini-cli
```

## Architecture

The project consists of three Docker images that can be used independently or together:

### 1. nezhar/gemini-container (gemini-cli/)

Node.js 22 Alpine container running the official `@google/gemini-cli` npm package. When used with the proxy, it routes all HTTPS traffic through the logging proxy.

- **Base:** node:22-alpine
- **Working Directory:** /workspace (mapped to current directory or custom workspace)
- **Credentials:** /root/.gemini (mapped to `~/.config/gemini-container/config`)
- **Proxy Certs:** /mitmproxy (mapped to `~/.config/gemini-container/proxy` when proxy is enabled)

### 2. nezhar/gemini-proxy (gemini-proxy/)

Python 3.11 Slim container with mitmproxy that intercepts HTTPS requests to `generativelanguage.googleapis.com` and logs:
- Request URL, method, headers, and body
- Response status code, headers, and body

Data is stored in a SQLite database (`logs.db`) at `~/.config/gemini-container/proxy` on the host, shared with the Datasette service.

- **Base:** python:3.11-slim
- **Port:** 8080
- **Data Directory:** /app (mapped to `~/.config/gemini-container/proxy`)

### 3. nezhar/gemini-datasette (gemini-datasette/)

Python 3.11 Slim container with Datasette for exploring the logged API requests. Provides filtering, sorting, custom SQL queries, and data export capabilities.

- **Base:** python:3.11-slim
- **Port:** 8001
- **Data Directory:** /app

## Troubleshooting

### Credentials not working

If authentication fails despite having valid credentials:

1. Ensure `~/.config/gemini-container/config/google_accounts.json` and `~/.config/gemini-container/config/settings.json` exist
2. Try re-authenticating if tokens have expired
3. Check file permissions: `chmod -R 755 ~/.config/gemini-container`

### Docker not found

Ensure Docker is installed and running:

```bash
docker --version
```

### Port conflicts

If ports 8080 or 8001 are already in use:

```bash
# Use custom ports
gemini-container --proxy-port 9090 --datasette-port 9001 --proxy --datasette "query"
```

### Proxy certificate issues

If you see SSL/TLS errors when using `--proxy`:

1. **Certificate not generated**: The proxy may need more time to initialize. Wait 30 seconds and try again.

2. **Stale certificate**: Clean up and regenerate:
   ```bash
   gemini-container --cleanup
   rm -rf ~/.config/gemini-container/proxy/.mitmproxy
   # Then run again with --proxy
   ```

3. **Check certificate exists**:
   ```bash
   ls -la ~/.config/gemini-container/proxy/.mitmproxy/mitmproxy-ca-cert.pem
   ```

4. **Check proxy logs**:
   ```bash
   docker logs gemini-proxy
   ```
