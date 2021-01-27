# HTTP File Server

## Basic

```bash
python -m http.server 8000
```

## HTTPS

* Sample

```python
#!/usr/bin/env python3 

# taken from http://www.piware.de/2011/01/creating-an-https-server-in-python/
# generate server.xml with the following command:
#    openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
# run as follows:
#    python simple-https-server.py
# then in your browser, visit:
#    https://localhost:4443

import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler 
import ssl


PORT=4443

parser = argparse.ArgumentParser(description='HTTP Options')
parser.add_argument('--ip', '-i', type=str, default='0.0.0.0', required=False)
parser.add_argument('--port', '-p', type=int, default=PORT, required=False)
parser.add_argument('--cert', '-c', type=str, required=True)
parser.add_argument('--key', '-k', type=str, required=True)
args, _ = parser.parse_known_args()
IP = args.ip
PORT = args.port
CERT = args.cert
KEY = args.key


httpd = HTTPServer(
    (IP, PORT),
    SimpleHTTPRequestHandler,
)
httpd.socket = ssl.wrap_socket(
    httpd.socket,
    keyfile=KEY,
    certfile=CERT,
    server_side=True,
)

if __name__ == "__main__":
    httpd.serve_forever()
```
