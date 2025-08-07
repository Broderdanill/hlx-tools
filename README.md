# hlx-tools
Tools for Helix (replacement for plugins coded for plugin server)


podman build -t hlx-tools -f Containerfile .
podman run -d -p 8000:8000 hlx-tools


Test Cases

urlencode
-------------------------
curl -X POST http://localhost:8000/urlencode \
  -H "Content-Type: application/json" \
  -d '{"text": "Hej på dig!"}'


urldecode
-------------------------
curl -X POST http://localhost:8000/urldecode \
  -H "Content-Type: application/json" \
  -d '{"text": "Hej%20p%C3%A5%20dig%21"}'


random number
-------------------------
curl "http://localhost:8000/random-number?from=0&to=200"


json_selector
-------------------------
curl -X POST http://localhost:8000/json-selector \
  -H "Content-Type: application/json" \
  -d '{"json_data": {"user": {"name": "Anna", "age": 30}}, "selector": "$.user.name"}'


file_to_base64
-------------------------
curl -X POST http://localhost:8000/file-to-base64 \
  -H "Content-Type: multipart/form-data" \
  -F "file=@testfile.txt"


strip_html
-------------------------
curl -X POST http://localhost:8000/strip-html \
  -H "Content-Type: application/json" \
  -d '{"html": "<html><body><h1>Rubrik</h1><p>Text med <b>fetstil</b>.</p></body></html>"}'
