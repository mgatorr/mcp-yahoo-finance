<p align="center">
  <img src="assets/hero.png" alt="mcp-yahoo-finance — free worldwide market data for Claude, with an illiquid-symbol crash fix" width="100%">
</p>

> ### About this fork
> This is a fork of [**maxscheijen/mcp-yahoo-finance**](https://github.com/maxscheijen/mcp-yahoo-finance)
> (MIT, © Max Scheijen) maintained for [**claude-mcp-stack**](https://github.com/mgatorr/claude-mcp-stack).
> It adds a robustness fix: `get_current_stock_price` no longer crashes with
> `Unknown format code 'f' for object of type 'str'` on illiquid symbols (e.g. `OD7C.DE`)
> whose `.info` exposes no numeric last price. The value is coerced, falls back to the last
> available close, and otherwise returns a clear `No price data available for <symbol>`.
> Pinned release: **`v0.1.3-mcpstack.1`**. The upstream MIT license and attribution are
> preserved; the original README follows below.

---

# MCP Yahoo Finance

![PyPI - Version](https://img.shields.io/pypi/v/mcp-yahoo-finance)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mcp-yahoo-finance)
![PyPI - License](https://img.shields.io/pypi/l/mcp-yahoo-finance)


A [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server for Yahoo Finance interaction. This server provides tools to get pricing, company information and more.

> Please note that `mcp-yahoo-finance` is currently in early development. The functionality and available tools are subject to change and expansion as I continue to develop and improve the server.

## Installation

You don't need to manually install `mcp-yahoo-finance` if you use [`uv`](https://docs.astral.sh/uv/). We'll use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run `mcp-yahoo-finance`.

I would recommend using this method if you simply want to use the MCP server.

### Using pip

Using `pip`.

```sh
pip install mcp-yahoo-finance
```

### Using Git

You can also install the package after cloning the repository to your machine.

```sh
git clone git@github.com:maxscheijen/mcp-yahoo-finance.git
cd mcp-yahoo-finance
uv sync
```

## Configuration

### Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
    "mcpServers": {
        "yahoo-finance": {
            "command": "uvx",
            "args": ["mcp-yahoo-finance"]
        }
    }
}
```
You can also use docker:

```json
{
    "mcpServers": {
        "yahoo-finance": {
            "command": "docker",
            "args": ["run", "-i", "--rm", "IMAGE"]
        }
    }
}
```

### VSCode

Add this to your `.vscode/mcp.json`:

```json
{
    "servers": {
        "yahoo-finance": {
            "command": "uvx",
            "args": ["mcp-yahoo-finance"]
        }
    }
}
```

## Examples of Questions

1. "What is the stock price of Apple?"
2. "What is the difference in stock price between Apple and Google?"
3. "How much did the stock price of Apple change between 2024-01-01 and 2025-01-01?"
4. "What are the available options expiration dates for AAPL?"
5. "Show me the options chain for AAPL expiring on 2024-01-19"
6. "What are the call and put options for Tesla?"

## Build

Docker:

```sh
docker build -t [IMAGE] .
```

## Test with MCP Inspector

```sh
npx @modelcontextprotocol/inspector uv run mcp-yahoo-finance
```
