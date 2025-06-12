# ocm-mcp

MCP server for Red Hat OpenShift Cluster Manager

## Running with Podman or Docker

You can run the ocm-mcp server in a container using Podman or Docker. Make sure you have a valid OCM token, which you can obtain by logging into https://console.redhat.com/openshift/token:

Example configuration for running with Podman:

```json
{
  "mcpServers": {
    "ocm-mcp": {
      "command": "podman",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "ACCESS_TOKEN_URL",
        "-e", "OCM_CLIENT_ID",
        "-e", "OCM_OFFLINE_TOKEN",
        "-e", "MCP_TRANSPORT",
        "quay.io/redhat-ai-tools/ocm-mcp"
      ],
      "env": {
        "ACCESS_TOKEN_URL": "https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token",
        "OCM_CLIENT_ID": "cloud-services",
        "OCM_OFFLINE_TOKEN": "REDACTED",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

## Running with non-stdio transport

To run the server with a non-stdio transport (such as SSE), set the `MCP_TRANSPORT` environment variable to a value other than `stdio` (e.g., `sse`).

Example configuration to connect to a non-stdio MCP server:

```json
{
  "mcpServers": {
    "slack": {
      "url": "https://ocm-mcp.example.com/sse",
      "headers": {
        "X-OCM-Offline-Token": "REDACTED"
      }
    }
  }
}
```

Replace `REDACTED` with the value from https://console.redhat.com/openshift/token.
