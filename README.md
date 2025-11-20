# Gemini Container

This project provides a Docker container for running the Gemini CLI, providing an isolated and consistent environment.

## Prerequisites

Copy the Gemini CLI credentials from this project's `auth/` folder to `~/.gemini/` on your host:

```bash
mkdir -p ~/.gemini
cp auth/google_accounts.json ~/.gemini/
cp auth/settings.json ~/.gemini/
```

## Build the Image

```bash
docker build -t gemini-container .
```

## Run the Container

Run the Gemini CLI by mounting your workspace and local credentials:

```bash
docker run --rm -it -v "$(pwd):/app" -v ~/.gemini:/root/.gemini:ro gemini-container
```

## Docker Compose

Alternatively, build the image using docker compose:

```bash
docker compose build
```

## Alternative: API Key Authentication

If you prefer not to use OAuth credentials, you can use an API key:

```bash
docker run --rm -it -v "$(pwd):/app" -e GEMINI_API_KEY=your-api-key gemini-container
```

**Note:** API key authentication only provides access to the basic Flash model, not Pro models.

## Troubleshooting

### Credentials not working

If authentication fails despite having valid credentials:

1. Ensure `~/.gemini/google_accounts.json` and `~/.gemini/settings.json` exist on your host
2. Try re-authenticating if the tokens have expired

### Permission issues

If you get permission errors, ensure the credentials directory is readable:

```bash
chmod -R 755 ~/.gemini
```
