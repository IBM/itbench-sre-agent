import logging
import json
import os
import re
import time
from typing import Any, Dict, Optional, Type

from crewai.tools.base_tool import BaseTool
from pydantic import BaseModel, ConfigDict, Field

from lumyn.tools.linting.promql_linter import PromQLLinter

from .grafana_base_client import GrafanaBaseClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class NL2MetricsCustomToolInput(BaseModel):
    nl_query: str = Field(
        title="PromQL Query",
        description="PromQL query to execute.",
    )


class NL2MetricsCustomTool(BaseTool, GrafanaBaseClient):
    name: str = "NL2Metrics Tool"
    description: str = "Converts natural language to PromQL queries and execute them to access metrics from Prometheus via the Grafana API. When using the NL2Metrics Tool you could ask queries like: get the average CPU usage of a pod-456 in namespace complex-us over the last hour get the network received bytes of a pod-789 in namespace simple-us over the last 10 minutes get the total memory utilization by the deployment called front in namespace simple-us currently"
    llm_backend: Any = None
    args_schema: Type[BaseModel] = NL2MetricsCustomToolInput

    def _run(self, nl_query: str) -> str:
        GrafanaBaseClient.model_post_init(self)
        try:
            function_arguments = self._generate_promql_query(prompt=nl_query)
            lint_message = PromQLLinter.lint(function_arguments)
            if lint_message != function_arguments:
                return lint_message
            return self._summarize_metrics(self._query_prometheus_metrics(function_arguments))
        except Exception as exc:
            logger.error(f"NL2Metrics Tool failed with: {exc}")
            return f"NL2Metrics Tool failed with: {exc}"

    def _generate_promql_query(self, prompt: str) -> str:

        with open(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "in_context_examples",
                             "grafana_prometheus.txt"), "r") as f:
            prom_icl = f.read()

        time_in_seconds = time.time()
        input = f"{prom_icl}\n\nWrite a promql query to do the following: {prompt}\n\nThe current time in seconds is {time_in_seconds}"
        system_prompt = "You write PromQL queries. Answer with only the correct PromQL query. The formatting should always be like this: ```promql\n<promql query>\n```"
        function_arguments = self.llm_backend.inference(system_prompt, input)
        logger.info(f"NL2Metrics Tool NL prompt received: {prompt}")
        logger.info(f"NL2Metrics Tool function arguments identified are: {function_arguments}")
        print(f"NL2Metrics Tool NL prompt received: {prompt}")
        print(f"NL2Metrics Tool function arguments identified are: {function_arguments}")
        response = re.search(r"```promql\n(.*?)\n```", function_arguments, re.DOTALL).group(1).strip()
        return response

    def _query_prometheus_metrics(self, query: str) -> Optional[Dict[str, Any]]:
        try:
            datasource_id = self.get_datasource_id("prometheus")
            url = f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_id}/api/v1/query"
            params = {"query": query}

            response = self._make_request("GET", url, params=params)
            logger.info(f"NL2Metrics Tool query prometheus metrics: {response.status_code}")
            print(f"NL2Metrics Tool query prometheus metrics: {response.content}")
            return response.json()
        except Exception as e:
            print(f"Error querying Prometheus metrics: {str(e)}")
            logger.error(f"Error querying Prometheus metrics: {str(e)}")
            return f"Error querying Prometheus metrics: {str(e)}"

    def _summarize_metrics(self, metrics):
        system_prompt = "You do metrics analysis and summarization. Look at the metrics given to you and provide a brief summary and analysis of them."
        metrics_summary = self.llm_backend.inference(system_prompt, json.dumps(metrics))
        return metrics_summary