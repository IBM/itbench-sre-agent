import json
import logging
from typing import Any, Dict, Optional

from crewai.tools.base_tool import BaseTool

from .grafana_base_client import GrafanaBaseClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class GetTopologyNodes(BaseTool, GrafanaBaseClient):
    name: str = "GetTopology Tool"
    description: str = "Get topology nodes describing the current IT environment."

    def _run(self) -> str:
        GrafanaBaseClient.model_post_init(self)
        data = None
        try:
            if "127.0.0.1" in self.grafana_url:
                url = f"{self.topology_url}/nodes"
            else:
                base_url = "/".join(f"{self.grafana_url}".split('/')[:-1])
                url = f"{base_url}/topology/nodes"
            response = self._make_request("GET", url)
            logger.info(f"GetTopologyNodesTool: {response.status_code}")
            logger.info(f"GetTopologyNodesTool: {response.content}")
            print(f"GetTopologyNodesTool: {response.status_code}")
            print(f"GetTopologyNodesTool: {response.content}")
            data = response.json()
            if response.status_code == 200:
                return data
            return None
        except Exception as e:
            print(f"Error querying Topology Nodes API: {str(e)}")
            logger.error(f"Error querying Topology Nodes API: {str(e)}")
            return None