# hlx-tools
Tools for Helix (replacement for plugins coded for plugin server)


podman build -t hlx-tools -f Containerfile .
podman run -d -p 8000:8000 hlx-tools


curl -X POST http://localhost:8000/urlencode -H "Content-Type: application/json" -d '{"text": "Hej på dig!"}'
