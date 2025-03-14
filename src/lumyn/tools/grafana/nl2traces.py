import json
import logging
import os
import time
from typing import Any, Dict, Optional, Type

from crewai.tools.base_tool import BaseTool
from pydantic import BaseModel, ConfigDict, Field

from lumyn.tools.linting.jaeger_linter import JaegerLinter

from .custom_function_definitions_grafana import fd_query_jaeger_traces
from .grafana_base_client import GrafanaBaseClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class NL2TracesCustomToolInput(BaseModel):
    nl_query: str = Field(
        title="NL Query",
        description=
        "Natural language query to be converted to function arguments.",
    )


class NL2TracesCustomTool(BaseTool, GrafanaBaseClient):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "NL2Traces Tool"
    description: str = "Take in a natural language query or utterance and turn it into function arguments. This tool is for gathering traces from jaeger. When using NL2Traces Tool you could ask queries like: retrieve traces for payment-service for the last hour get traces for test-service for the last 15 minutes get GET traces for back-service for the last 15 minutes get POST traces from ticket-service for the last 5 minutes get POST traces from <service-name> for the last X minutes"
    llm_backend: Any = None
    args_schema: Type[BaseModel] = NL2TracesCustomToolInput

    def _run(self, nl_query: str) -> str:
        GrafanaBaseClient.model_post_init(self)
        try:
            function_name, function_arguments, current_time = self._generate_jaeger_query(
                prompt=nl_query)
            services = self._get_services()
            operations = self._get_operations(function_arguments['service'])
            lint_message = JaegerLinter().lint(function_arguments, services,
                                               operations, current_time)
            if lint_message != function_arguments:
                return lint_message
            return self._summarize_traces(self._query_jaeger_traces(**function_arguments))
        except Exception as exc:
            logger.error(f"NL2Traces Tool failed with: {exc}")
            return f"NL2Traces Tool failed with: {exc}"

    def _generate_jaeger_query(self, prompt: str) -> str:

        with open(
                os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "in_context_examples", "grafana_jaeger.txt"),
                "r") as f:
            jaeger_icl = f.read()

        time_micro = int(time.time_ns() / 1000)
        input = f"{jaeger_icl}\n\nProvide the correct tool call for this action: {prompt}\n\nThe current time in microseconds is {time_micro}"

        system_prompt = "You are a function calling bot. You are given a prompt and you need to generate a tool call based on the prompt. Make sure to fill the parameters correctly. If no timeframe is given always get the last 10 minutes of traces."

        tools = [fd_query_jaeger_traces]

        function_name, function_arguments = self.llm_backend.function_calling_inference(
            system_prompt, input, tools)
        logger.info(f"NL2Traces Tool NL prompt received: {prompt}")
        logger.info(
            f"NL2Traces Tool function arguments identified are: {function_name} {function_arguments}"
        )
        return function_name, function_arguments, time_micro

    def _query_jaeger_traces(
            self,
            service: str,
            start_time: int,
            end_time: int,
            limit: int = 1,
            error_traces_only: bool = True,
            operation: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            datasource_id = self.get_datasource_id("jaeger")
            url = f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_id}/api/traces"
            if error_traces_only:
                params = {
                    "service": service,
                    "operation": operation,
                    "start": start_time,
                    "end": end_time,
                    "limit": 1,
                    "tags": json.dumps({"error": "true"})
                }
            else:
                params = {
                    "service": service,
                    "operation": operation,
                    "start": start_time,
                    "end": end_time,
                    "limit": 1
                }
            response = self._make_request("GET", url, params=params)
            logger.info(
                f"NL2Traces Tool query Jaeger traces: {response.status_code}"
            )
            logger.info(
                f"NL2Traces Tool query Jaeger traces: {response.content}")
            print(
                f"NL2Traces Tool query Jaeger traces: {response.status_code}"
            )
            print(
                f"NL2Traces Tool query Jaeger traces: {response.content}")
            return response.json()
        except Exception as e:
            print(f"Error querying Jaeger traces: {str(e)}")
            logger.error(f"Error querying Jaeger traces: {str(e)}")
            return f"Error querying Jaeger traces: {str(e)}"
        
    def _summarize_traces(self, traces):
        system_prompt = "You do trace analysis and summarization. Look at the traces given to you and provide a brief summary and analysis of them."
        traces_summary = self.llm_backend.inference(system_prompt, json.dumps(traces))
        return traces_summary
        
    def _get_services(self):
        try:
            datasource_id = self.get_datasource_id("jaeger")
            url = f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_id}/api/services"
            response = self._make_request("GET", url)
            logger.info(
                f"GetTracesFromGrafana get_services: {response.status_code}")
            logger.info(
                f"GetTracesFromGrafana get_services: {response.content}")
            print(f"GetTracesFromGrafana get_services: {response.status_code}")
            print(f"GetTracesFromGrafana get_services: {response.content}")
            return response.json()['data']
        except Exception as e:
            print(
                f"Error querying GetTracesFromGrafana get_services: {str(e)}")
            logger.error(
                f"Error querying GetTracesFromGrafana get_services: {str(e)}")
            return None

    def _get_operations(self, service):
        try:
            datasource_id = self.get_datasource_id("jaeger")
            url = f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_id}/api/operations"
            params = {"service": service}
            response = self._make_request("GET", url, params=params)
            logger.info(
                f"GetTracesFromGrafana get_operations: {response.status_code}")
            logger.info(
                f"GetTracesFromGrafana get_operations: {response.content}")
            print(
                f"GetTracesFromGrafana get_operations: {response.status_code}")
            print(f"GetTracesFromGrafana get_operations: {response.content}")
            return response.json()['data']
        except Exception as e:
            print(
                f"Error querying GetTracesFromGrafana get_operations: {str(e)}"
            )
            logger.error(
                f"Error querying GetTracesFromGrafana get_operations: {str(e)}"
            )
            return None