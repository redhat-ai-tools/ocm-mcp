import os
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ocm")

OCM_API_BASE = os.environ.get("OCM_API_BASE", "https://api.openshift.com")
MCP_TRANSPORT = os.environ.get("MCP_TRANSPORT", "stdio")


async def make_request(url: str) -> dict[str, Any] | None:
    client_id = os.environ["OCM_CLIENT_ID"]
    offline_token = (
        os.environ["OCM_OFFLINE_TOKEN"]
        if MCP_TRANSPORT == "stdio"
        else mcp.get_context().request_context.request.headers["X-OCM-Offline-Token"]
    )
    access_token_url = os.environ["ACCESS_TOKEN_URL"]
    data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "refresh_token": offline_token,
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(access_token_url, data=data, timeout=30.0)
            response.raise_for_status()
            token = response.json().get("access_token")
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            }
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(e)
            return None


@mcp.tool()
async def whoami() -> str:
    url = f"{OCM_API_BASE}/api/accounts_mgmt/v1/current_account"
    data = await make_request(url)
    if data:
        return data.get("username")
    return "Failed to fetch whoami data."


def format_clusters_response(data):
    if not data or "items" not in data:
        return "No clusters found or invalid response."

    lines = []
    for cluster in data["items"]:
        name = cluster.get("name", "N/A")
        cid = cluster.get("id", "N/A")
        api_url = cluster.get("api", {}).get("url", "N/A")
        console_url = cluster.get("console", {}).get("url", "N/A")
        state = cluster.get("state", "N/A")
        version = cluster.get("openshift_version", "N/A")
        lines.append(
            f"Cluster: {name}\n"
            f"  ID: {cid}\n"
            f"  API URL: {api_url}\n"
            f"  Console URL: {console_url}\n"
            f"  State: {state}\n"
            f"  Version: {version}\n"
        )
    return "\n".join(lines)


def format_clusters_response_logs(data):
    if not data or "items" not in data:
        return "No clusters found or invalid response."

    lines = []
    for cluster in data["items"]:
        service_name = cluster.get("service_name", "N/A")
        cid = cluster.get("id", "N/A")
        description = cluster.get("description", "")

        lines.append(
            f"  Cluster: {service_name}\n"
            f"  ID: {cid}\n"
            f"  DESCRIPTION: {description}\n"
        )
    return "\n".join(lines)


def format_addons_response(data):
    if not data or "items" not in data:
        return "No addons found or invalid response."

    lines = []
    for addon in data["items"]:
        name = addon.get("name", "N/A")
        state = addon.get("state", "N/A")
        lines.append(f"Addon: {name}\n" f"  State: {state}\n")
    return "\n".join(lines)


def format_machine_pools_response(data):
    if not data or "items" not in data:
        return "No machine pools found or invalid response."

    lines = []
    for machine_pool in data["items"]:
        id = machine_pool.get("id", "N/A")
        replicas = machine_pool.get("replicas", "N/A")
        instance_type = machine_pool.get("instance_type", "N/A")
        lines.append(f"Machine Pool: {id}\n  Replicas: {replicas}\n  Instance Type: {instance_type}\n")
    return "\n".join(lines)


@mcp.tool()
async def get_clusters(state: str) -> str:
    url = f"{OCM_API_BASE}/api/clusters_mgmt/v1/clusters"
    data = await make_request(url)

    formatted = format_clusters_response(data)
    return formatted


@mcp.tool()
async def get_cluster(cluster_id: str) -> str:
    url = f"{OCM_API_BASE}/api/clusters_mgmt/v1/clusters/{cluster_id}"
    data = await make_request(url)
    if data and data.get("id"):
        return format_clusters_response({"items": [data]})


@mcp.tool()
async def get_clusters_logs(cluster_id: str) -> str:
    url = f"{OCM_API_BASE}/api/service_logs/v1/clusters/cluster_logs?cluster_id={cluster_id}"
    data = await make_request(url)
    if data:
        return format_clusters_response_logs(data)
    return "No logs found or invalid response."


@mcp.tool()
async def get_cluster_addons(cluster_id: str) -> str:
    url = f"{OCM_API_BASE}/api/clusters_mgmt/v1/clusters/{cluster_id}/addons"
    data = await make_request(url)
    if data:
        return format_addons_response(data)
    return "Failed to fetch addons data."


@mcp.tool()
async def get_cluster_machine_pools(cluster_id: str) -> str:
    url = f"{OCM_API_BASE}/api/clusters_mgmt/v1/clusters/{cluster_id}/machine_pools"
    data = await make_request(url)
    if data:
        return format_machine_pools_response(data)
    return "Failed to fetch machine pools data."


if __name__ == "__main__":
    mcp.run(transport=os.environ.get("MCP_TRANSPORT", "stdio"))
