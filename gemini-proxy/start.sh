#!/bin/sh
set -e

# Generate cert if it doesn't exist
if [ ! -f /app/.mitmproxy/mitmproxy-ca-cert.pem ]; then
  echo "Generating mitmproxy certificate..."
  mitmdump -p 8080 &
  sleep 3
  if [ -f ~/.mitmproxy/mitmproxy-ca-cert.pem ]; then
    cp ~/.mitmproxy/mitmproxy-ca-cert.pem /app/.mitmproxy/
  else
    echo "mitmproxy certificate not found."
    exit 1
  fi
  killall mitmdump
  echo "Certificate generated."
fi

# Start the proxy
echo "Starting proxy..."
mitmdump -p 8080 -s proxy.py
