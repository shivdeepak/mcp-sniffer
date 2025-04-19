import argparse
import asyncio
import os

from mcp_sniffer.config import AppConfig
from mcp_sniffer.main import mcp_sniffer


def parse_args() -> AppConfig:
    parser = argparse.ArgumentParser(description="MCP Sniffer")

    parser.add_argument(
        "--listen-host",
        default=os.getenv("LISTEN_HOST", "127.0.0.1"),
        help="Host to listen on (default: env LISTEN_HOST or 127.0.0.1)",
    )
    parser.add_argument(
        "--listen-port",
        type=int,
        default=int(os.getenv("LISTEN_PORT", "3002")),
        help="Port to listen on (default: env LISTEN_PORT or 3002)",
    )
    parser.add_argument(
        "--upstream-host",
        default=os.getenv("UPSTREAM_HOST", "127.0.0.1"),
        help="Upstream host (default: env UPSTREAM_HOST or 127.0.0.1)",
    )
    parser.add_argument(
        "--upstream-port",
        type=int,
        default=int(os.getenv("UPSTREAM_PORT", "3001")),
        help="Upstream port (default: env UPSTREAM_PORT or 3001)",
    )
    parser.add_argument(
        "--web-ui-host",
        default=os.getenv("WEB_UI_HOST", "127.0.0.1"),
        help="Web UI host (default: env WEB_UI_HOST or 127.0.0.1)",
    )
    parser.add_argument(
        "--web-ui-port",
        type=int,
        default=int(os.getenv("WEB_UI_PORT", "8888")),
        help="Web UI port (default: env WEB_UI_PORT or 8888)",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("LOG_LEVEL", "INFO"),
        help="Log level (default: env LOG_LEVEL or INFO)",
    )

    args = parser.parse_args()
    return AppConfig(
        LISTEN_HOST=args.listen_host,
        LISTEN_PORT=args.listen_port,
        UPSTREAM_HOST=args.upstream_host,
        UPSTREAM_PORT=args.upstream_port,
        WEB_UI_HOST=args.web_ui_host,
        WEB_UI_PORT=args.web_ui_port,
    )


def main():
    config = parse_args()
    try:
        asyncio.run(mcp_sniffer(config))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
