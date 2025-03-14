import json
import logging
from typing import Any, Dict, Optional

from crewai.tools.base_tool import BaseTool

from .grafana_base_client import GrafanaBaseClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class GetAlertsCustomTool(BaseTool, GrafanaBaseClient):
    name: str = "GetAlerts Tool"
    description: str = "Get alerts on the IT environment at present time via the Grafana API."

    def _run(self) -> str:
        GrafanaBaseClient.model_post_init(self)
        data = None
        try:
            url = f"{self.grafana_url}/api/prometheus/grafana/api/v1/alerts"
            response = self._make_request("GET", url)
            logger.info(f"GetAlertsCustomTool: {response.status_code}")
            logger.info(f"GetAlertsCustomTool: {response.content}")
            print(f"GetAlertsCustomTool: {response.status_code}")
            print(f"GetAlertsCustomTool: {response.content}")
            data = response.json()
            if response.status_code == 200:
                if len(data["data"]["alerts"]) == 0:
                    return None
                alerts = list(filter(lambda i: i["state"] == "Alerting", data["data"]["alerts"]))
                return alerts
            return None
        except Exception as e:
            print(f"Error querying Grafana Alerts API: {str(e)}")
            logger.error(f"Error querying Grafana Alerts API: {str(e)}")
            return None
 