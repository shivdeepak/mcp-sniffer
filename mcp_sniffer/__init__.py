from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("mcp-sniffer")
except PackageNotFoundError:
    __version__ = "unknown"
