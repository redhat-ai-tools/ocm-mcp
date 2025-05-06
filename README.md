# ocm-mcp

MCP server for Red Hat OpenShift Cluster Manager

## Running with Podman or Docker

You can run the ocm-mcp server in a container using Podman or Docker. Make sure you have a valid OCM access token, which you can obtain by running `ocm login` and then `ocm token`:

```sh
ocm login --token=YOUR_OFFLINE_TOKEN
export OCM_TOKEN=$(ocm token)
```

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
        "-e", "OCM_TOKEN",
        "quay.io/maorfr/ocm-mcp"
      ],
      "env": {
        "OCM_TOKEN": "REDACTED"
      }
    }
  }
}
```

Replace `REDACTED` with the value from `ocm token`.
