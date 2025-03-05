# Copyright contributors to the ITBench project. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import re
import json
import logging
from typing import Dict, Optional, Tuple
import litellm
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

class LiteLLMBackend():
    def __init__(self, 
                 provider: str,
                 model_name: str,
                 base_url: str,
                 api_key: str,
                 api_version: str,
                 seed: int,
                 top_p: float,
                 temperature: float,
                 reasoning_effort: str,
                 is_native_function_calling_supported: bool,
                 extra_headers: Optional[Dict[str, str]] = None):
        self.provider = provider
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key
        self.api_version = api_version
        self.temperature = temperature
        self.seed = seed
        self.top_p = top_p
        self.reasoning_effort = reasoning_effort
        self.is_native_function_calling_supported = is_native_function_calling_supported
        self.extra_headers = extra_headers
        litellm.drop_params = True
        self.FOR_NON_NATIVE_FUNCTION_CALLING = """
        If you choose to call a function ONLY reply in the following format with no prefix or suffix:

        <function=example_function_name>{\"example_name\": \"example_value\"}</function>

        Please remember to:
        - Follow the specified format, start with <function= and end with </function>
        - Required parameters MUST be specified
        - Only call one function at a time
        - Put the entire function call reply on one line
        - If there is no function call available, answer the question like normal with your current knowledge and do not tell the user about function calls
        """
    
    def parse_tool_response(self, response: str):
        function_regex = r"<function=(\w+)>(.*?)</function>"
        match = re.search(function_regex, response)

        if match:
            function_name, args_string = match.groups()
            try:
                args = json.loads(args_string)
                return function_name, args
            except json.JSONDecodeError as error:
                print(f"Error parsing function arguments: {error}")
                return None, None
        return None, None

    def inference(self, system_prompt: str, input: str) -> str:
        logger.info(f"NL input received: {input}")
        print(f"NL input received: {input}")

        kwargs = {
            "model": f"{self.provider}/{self.model_name}",
            "api_key": self.api_key,
            "api_base": self.base_url,
            "api_version": self.api_version,
            "seed": self.seed,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "reasoning_effort": self.reasoning_effort,
            "extra_headers": self.extra_headers
        }

        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user", 
                "content": input
            }
        ]

        kwargs["messages"] = messages

        completion = litellm.completion(**kwargs)
        return completion.choices[0].message.content

    def function_calling_inference(self,
                                   system_prompt: str,
                                   input: str,
                                   tools: Optional[Dict] = None) -> Tuple[str, Dict]:
        logger.info(f"NL input received: {input}")
        print(f"NL input received: {input}")

        kwargs = {
            "model": f"{self.provider}/{self.model_name}",
            "api_key": self.api_key,
            "api_base": self.base_url,
            "api_version": self.api_version,
            "seed": self.seed,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "reasoning_effort": self.reasoning_effort,
            "extra_headers": self.extra_headers
        }

        if self.is_native_function_calling_supported:
            kwargs["tools"] = tools
        else:
            system_prompt = system_prompt + "\n" + self.FOR_NON_NATIVE_FUNCTION_CALLING

        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": input
            }
        ]

        kwargs["messages"] = messages

        completion = litellm.completion(**kwargs)

        finish_reason = completion.choices[0].finish_reason
        if finish_reason == "tool_calls":
            function_name = completion.choices[0].message.tool_calls[0].function.name
            function_arguments = json.loads(completion.choices[0].message.tool_calls[0].function.arguments)
            
            logger.info(
                f"function arguments identified are: {function_name} {function_arguments}"
            )
            print(
                f"function arguments identified are: {function_name} {function_arguments}"
            )
            return function_name, function_arguments
        elif finish_reason == "stop":
            function_name, function_arguments = self.parse_tool_response(
                completion.choices[0].message.content)
            if function_name is not None and function_arguments is not None:
                logger.info(
                    f"function arguments via stop identified are: {function_name} {function_arguments}"
                )
                print(
                    f"function arguments via stop identified are: {function_name} {function_arguments}"
                )
                return function_name, function_arguments

        logger.info(f"unsuccessful finish reason is: {finish_reason}")
        print(f"unsuccessful finish reason is: {finish_reason}")
        return None, None
