# MCP Sniffer

**MCP Sniffer** captures network traffic between MCP clients and servers.

It runs as a reverse proxy between the client and server, capturing request and response payloads that can be visualized in a web UI.

The following diagram shows how MCP Sniffer fits into the MCP Client-Server Model.

![Flow Diagram](https://raw.githubusercontent.com/shivdeepak/mcp-sniffer/main/docs/images/flow-diag.png)

For the Web UI - Imagine [Google Chrome DevTools'](https://developer.chrome.com/docs/devtools) Network Tab for [Model Context Protocol](https://modelcontextprotocol.io/).

Following is a very early version of it.

![Browse Connections](https://raw.githubusercontent.com/shivdeepak/mcp-sniffer/main/docs/images/webui.png)

![PyPI - License](https://img.shields.io/pypi/l/mcp-sniffer)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mcp-sniffer)

## Install

```shell
pipx install mcp-sniffer
```

## Usage

```
$ mcp-sniffer --help
usage: mcp-sniffer [-h] [--listen-host LISTEN_HOST] [--listen-port LISTEN_PORT] [--upstream-host UPSTREAM_HOST]
                   [--upstream-port UPSTREAM_PORT] [--web-ui-host WEB_UI_HOST] [--web-ui-port WEB_UI_PORT]
                   [--log-level LOG_LEVEL]

MCP Sniffer

options:
  -h, --help            show this help message and exit
  --listen-host LISTEN_HOST
                        Host to listen on (default: env LISTEN_HOST or 127.0.0.1)
  --listen-port LISTEN_PORT
                        Port to listen on (default: env LISTEN_PORT or 3002)
  --upstream-host UPSTREAM_HOST
                        Upstream host (default: env UPSTREAM_HOST or 127.0.0.1)
  --upstream-port UPSTREAM_PORT
                        Upstream port (default: env UPSTREAM_PORT or 3001)
  --web-ui-host WEB_UI_HOST
                        Web UI host (default: env WEB_UI_HOST or 127.0.0.1)
  --web-ui-port WEB_UI_PORT
                        Web UI port (default: env WEB_UI_PORT or 8888)
  --log-level LOG_LEVEL
                        Log level (default: env LOG_LEVEL or INFO)
```

## Run

```shell
mcp-sniffer --listen-port 3002 --upstream-port 3001
# INFO:     Started server process [32580]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# 2025-04-19 00:25:04 devmachine.local mcp_sniffer.proxy[32580] INFO Listening on ('127.0.0.1', 3002)...
# INFO:     Uvicorn running on http://127.0.0.1:8888 (Press CTRL+C to quit)
# INFO:     127.0.0.1:52396 - "GET / HTTP/1.1" 200 OK
# INFO:     127.0.0.1:52396 - "GET /assets/index-C93YJcsR.css HTTP/1.1" 200 OK
# INFO:     127.0.0.1:52397 - "GET /assets/index-CwtNIZdB.js HTTP/1.1" 200 OK
# INFO:     127.0.0.1:52397 - "GET /connections HTTP/1.1" 200 OK
```

## Web UI

Visit [http://127.0.0.1:8888](http://127.0.0.1:8888).

**Setup**
![Setup](https://raw.githubusercontent.com/shivdeepak/mcp-sniffer/main/docs/images/setup.png)

