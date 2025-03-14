import json
import logging
import os
import time
from typing import Any, Dict, Optional, Type

from crewai.tools.base_tool import BaseTool
from pydantic import BaseModel, Field

from lumyn.tools.linting.logql_linter import LogQLLinter

from .custom_function_definitions_grafana import fd_query_loki_logs
from .grafana_base_client import GrafanaBaseClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class NL2LogsCustomToolInput(BaseModel):
    nl_query: str = Field(
        title="NL Query",
        description="NL query to execute.",
    )


class NL2LogsCustomTool(BaseTool, GrafanaBaseClient):
    name: str = "NL2Logs Tool"
    description: str = "Converts natural language to LogQL queries and executes them to access logs (and other information) from Loki via the Grafana API. When using the NL2Logs Tool you could ask queries like: get the logs from the payment deployment get the logs from the worker-node-1 kubernetes host get the logs from the payment service with label app=payment NL2Logs only works for logs from services using their app name."
    llm_backend: Any = None
    args_schema: Type[BaseModel] = NL2LogsCustomToolInput

    def _run(self, nl_query: str) -> str:
        GrafanaBaseClient.model_post_init(self)
        try:
            function_name, function_arguments = self._generate_logql_query(
                prompt=nl_query)
            lint_message = LogQLLinter.lint(function_arguments)
            if lint_message != function_arguments:
                return lint_message
            return self._summarize_logs(self._query_loki_logs(**function_arguments))
        except Exception as exc:
            logger.error(f"NL2Logs Tool failed with: {exc}")
            return f"NL2Logs Tool failed with: {exc}"

    def _generate_logql_query(self, prompt: str) -> str:

        with open(
                os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "in_context_examples", "grafana_loki.txt"),
                "r") as f:
            loki_icl = f.read()
        logger.info(f"NL2Logs Tool NL prompt received: {prompt}")
        print(f"NL2Logs Tool NL prompt received: {prompt}")

        time_nano = time.time_ns()

        
        input = f"{loki_icl}\n\nWrite a LogQL query to do the following and return it in a tool call to query_loki_logs: {prompt}.\n\nHere is a dictionary of the values available for each label in the query {self._get_label_value_dict()} \n\nThe current time in nanoseconds is {time_nano}"
        
        
        tools = [fd_query_loki_logs]
        system_prompt = "Provide the correct tool call for querying loki logs using parameters provided in the input. For the LogQL query generate it using the input as instructions. Do not wrap the LogQL query in any tags or special formatting."
        function_name, function_arguments = self.llm_backend.function_calling_inference(
            system_prompt, input, tools)
        
        logger.info(
            f"NL2Logs Tool function arguments identified are: {function_name} {function_arguments}"
        )
        
        print(
            f"NL2Logs Tool function arguments identified are: {function_name} {function_arguments}"
        )
        return function_name, function_arguments

    def _query_loki_logs(
            self,
            query: str,
            limit: int = 10,
            start: Optional[str] = None,
            end: Optional[str] = None,
            since: Optional[str] = None,
            step: Optional[str] = None,
            interval: Optional[str] = None,
            direction: str = "backward") -> Optional[Dict[str, Any]]:
        try:
            datasource_id = self.get_datasource_id("loki")
            url = f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_id}/loki/api/v1/query_range"
            params = {
                "query": query,
                "limit": 10,
                "start": start,
                "end": end,
                "since": since,
                "step": step,
                "interval": interval,
                "direction": direction
            }
            response = self._make_request("GET", url, params=params)
            logger.info(
                f"NL2Logs Tool query Loki logs: {response.status_code}")
            print(f"NL2Logs Tool query Loki logs: {response.content}")
            return response.json()
        except Exception as e:
            print(f"Error querying Loki logs: {str(e)}")
            logger.error(f"Error querying Loki logs: {str(e)}")
            return f"Error querying Loki logs: {str(e)} Here is a dictionary of the values available for each label in the query {self._get_label_value_dict()}"
        
    def _get_labels(self):
        try:
            datasource_id = self.get_datasource_id("loki")
            url = f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_id}/loki/api/v1/labels"
            response = self._make_request("GET", url)
            return response.json()['data']
        except Exception as e:
            print(f"Error querying Loki logs: {str(e)}")
            logger.error(f"Error querying Loki logs: {str(e)}")
            return f"Error querying Loki logs: {str(e)}"

    def _get_label_values(self, label):
        try:
            datasource_id = self.get_datasource_id("loki")
            url = f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_id}/loki/api/v1/label/{label}/values"
            response = self._make_request("GET", url)
            return response.json()['data']
        except Exception as e:
            print(f"Error querying Loki logs: {str(e)}")
            logger.error(f"Error querying Loki logs: {str(e)}")
            return f"Error querying Loki logs: {str(e)}"
        
    def _get_app_label_values(self):
        try:
            datasource_id = self.get_datasource_id("loki")
            url = f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_id}/loki/api/v1/label/app/values"
            response = self._make_request("GET", url)
            return response.json()['data']
        except Exception as e:
            print(f"Error querying Loki logs: {str(e)}")
            logger.error(f"Error querying Loki logs: {str(e)}")
            return f"Error querying Loki logs: {str(e)}"
        
    def _get_label_value_dict(self):
        try:
            datasource_id = self.get_datasource_id("loki")
            label_url = f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_id}/loki/api/v1/labels"
            response = self._make_request("GET", label_url)
            label_value_dict = {}
            for label in response.json()['data']:
                value_url = f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_id}/loki/api/v1/label/{label}/values"
                values = self._make_request("GET", value_url).json()['data']
                label_value_dict[label] = values
            return label_value_dict

        except Exception as e:
            print(f"Error querying Loki logs: {str(e)}")
            logger.error(f"Error querying Loki logs: {str(e)}")
            return f"Error querying Loki logs: {str(e)}"

    
    def _get_last_hour(self, application):
        try:
            datasource_id = self.get_datasource_id("loki")
            url = f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_id}/loki/api/v1/query_range"
            params = {
                "query": f"app='{application}'",
            }
            response = self._make_request("GET", url, params=params)
            logger.info(f"NL2Logs Tool query Loki logs: {response.status_code}")
            print(f"NL2Logs Tool query Loki logs: {response.content}")
            return response.json()
        except Exception as e:
            print(f"Error querying Loki logs: {str(e)}")
            logger.error(f"Error querying Loki logs: {str(e)}")
            return f"Error querying Loki logs: {str(e)}"
        
    def _summarize_logs(self, logs):
        system_prompt = "You do log analysis and summarization. Look at the logs given to you and provide a brief summary and analysis of them."
        logs_summary = self.llm_backend.inference(system_prompt, json.dumps(logs))
        return logs_summary