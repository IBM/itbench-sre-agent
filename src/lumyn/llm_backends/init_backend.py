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
from crewai import LLM
from dotenv import load_dotenv

from .litellm_backend import LiteLLMBackend

load_dotenv()

global LLM_PROVIDER_AGENT, LLM_MODEL_NAME_AGENT, LLM_BASE_URL_AGENT, LLM_API_VERSION_AGENT, LLM_API_KEY_AGENT, REASONING_EFFORT_AGENT, LLM_SEED_AGENT, LLM_TOP_P_AGENT, LLM_TEMPERATURE_AGENT
global LLM_PROVIDER_TOOLS, LLM_MODEL_NAME_TOOLS, LLM_BASE_URL_TOOLS, LLM_API_VERSION_TOOLS, LLM_API_KEY_TOOLS, REASONING_EFFORT_TOOLS, LLM_SEED_TOOLS, LLM_TOP_P_TOOLS, LLM_TEMPERATURE_TOOLS

try:
    LLM_PROVIDER_AGENT = os.environ["LLM_PROVIDER_AGENT"]
except KeyError:
    LLM_PROVIDER_AGENT = ""
    print(f"Unable to find environment variable - LLM_PROVIDER_AGENT.")
    raise

try:
    LLM_PROVIDER_TOOLS = os.environ["LLM_PROVIDER_TOOLS"]
except KeyError:
    LLM_PROVIDER_TOOLS = ""
    print(f"Unable to find environment variable - LLM_PROVIDER_TOOLS.")
    raise

try:
    LLM_MODEL_NAME_AGENT  = os.environ["LLM_MODEL_NAME_AGENT"]
except KeyError:
    LLM_MODEL_NAME_AGENT = ""
    print(f"Unable to find environment variable - LLM_MODEL_NAME_AGENT.")
    raise

try:
    LLM_MODEL_NAME_TOOLS = os.environ["LLM_MODEL_NAME_TOOLS"]
except KeyError:
    LLM_MODEL_NAME_TOOLS = ""
    print(f"Unable to find environment variable - LLM_MODEL_NAME.")
    raise

try:
    LLM_BASE_URL_AGENT = os.environ["LLM_BASE_URL_AGENT"].rstrip("/")
except KeyError:
    LLM_BASE_URL_AGENT = ""
    print(f"Unable to find environment variable - LLM_BASE_URL_AGENT.")
    raise

try:
    LLM_BASE_URL_TOOLS = os.environ["LLM_BASE_URL_TOOLS"].rstrip("/")
except KeyError:
    LLM_BASE_URL_TOOLS = ""
    print(f"Unable to find environment variable - LLM_BASE_URL_TOOLS.")
    raise

try:
    LLM_API_KEY_AGENT = os.environ["LLM_API_KEY_AGENT"]
except KeyError:
    print("Unable to find environment variable - LLM_API_KEY_AGENT.")
    raise

try:
    LLM_API_KEY_TOOLS = os.environ["LLM_API_KEY_TOOLS"]
except KeyError:
    print("Unable to find environment variable - LLM_API_KEY_TOOLS.")
    raise

try:
    LLM_SEED_AGENT = int(os.environ["LLM_SEED_AGENT"])
except KeyError:
    LLM_SEED_AGENT = 10
    print(f"Unable to find environment variable - LLM_SEED_AGENT. Defaulting to {LLM_SEED_AGENT}.")

try:
    LLM_SEED_TOOLS = int(os.environ["LLM_SEED_TOOLS"])
except KeyError:
    LLM_SEED_TOOLS = 10
    print(f"Unable to find environment variable - LLM_SEED_TOOLS. Defaulting to {LLM_SEED_TOOLS}.")

try:
    LLM_TOP_P_AGENT = float(os.environ["LLM_TOP_P_AGENT"])
except KeyError:
    LLM_TOP_P_AGENT = 0.95
    print(f"Unable to find environment variable - LLM_TOP_P_AGENT. Defaulting to {LLM_TOP_P_AGENT}.")

try:
    LLM_TOP_P_TOOLS = float(os.environ["LLM_TOP_P_TOOLS"])
except KeyError:
    LLM_TOP_P_TOOLS = 0.95
    print(f"Unable to find environment variable - LLM_TOP_P_TOOLS. Defaulting to {LLM_TOP_P_TOOLS}.")

try:
    LLM_TEMPERATURE_AGENT = float(os.environ["LLM_TEMPERATURE_AGENT"])
except KeyError:
    LLM_TEMPERATURE_AGENT = 0.0
    print(f"Unable to find environment variable - LLM_TEMPERATURE_AGENT. Defaulting to {LLM_TEMPERATURE_AGENT}.")
except ValueError as e:
    print("Incorrect LLM_TEMPERATURE_AGENT value:", e)
    raise

try:
    LLM_TEMPERATURE_TOOLS = float(os.environ["LLM_TEMPERATURE_TOOLS"])
except KeyError:
    LLM_TEMPERATURE_TOOLS = 0.0
    print(f"Unable to find environment variable - LLM_TEMPERATURE_TOOLS. Defaulting to {LLM_TEMPERATURE_TOOLS}.")
except ValueError as e:
    print("Incorrect LLM_TEMPERATURE_TOOLS value:", e)
    raise

try:
    REASONING_EFFORT_AGENT = str(os.environ["REASONING_EFFORT_AGENT"]).lower()
except KeyError:
    REASONING_EFFORT_AGENT = ""
    print(f"Unable to find environment variable - REASONING_EFFORT_AGENT.")

try:
    REASONING_EFFORT_TOOLS = str(os.environ["REASONING_EFFORT_TOOLS"]).lower()
except KeyError:
    REASONING_EFFORT_TOOLS = ""
    print(f"Unable to find environment variable - REASONING_EFFORT_TOOLS.")

try:
    LLM_API_VERSION_AGENT  = os.environ["LLM_API_VERSION_AGENT"]
except KeyError:
    LLM_API_VERSION_AGENT = ""
    print(f"Unable to find environment variable - LLM_API_VERSION_AGENT.")

try:
    LLM_API_VERSION_TOOLS  = os.environ["LLM_API_VERSION_TOOLS"]
except KeyError:
    LLM_API_VERSION_TOOLS = ""
    print(f"Unable to find environment variable - LLM_API_VERSION_TOOLS.")

try:
    IS_NATIVE_FUNCTION_CALLING_SUPPORTED  = os.environ["IS_NATIVE_FUNCTION_CALLING_SUPPORTED"]
except KeyError:
    IS_NATIVE_FUNCTION_CALLING_SUPPORTED = False
    print(f"Unable to find environment variable - IS_NATIVE_FUNCTION_CALLING_SUPPORTED.")

if LLM_PROVIDER_AGENT == "watsonx" or LLM_PROVIDER_TOOLS == "watsonx":
    try:
        os.environ["WX_PROJECT_ID"]
    except KeyError:
        print(f"To use WatsonX you must provide the WX_PROJECT_ID environment variable.")
        raise


def get_llm_backend_for_agents():
    if LLM_PROVIDER_AGENT.lower() == "rits":
        return LLM(model=f"openai/{LLM_MODEL_NAME_AGENT}",
                   base_url=LLM_BASE_URL_AGENT,
                   api_key="API_KEY",
                   api_version=LLM_API_VERSION_AGENT,
                   seed=LLM_SEED_AGENT,
                   top_p=LLM_TOP_P_AGENT,
                   temperature=LLM_TEMPERATURE_AGENT,
                   reasoning_effort=REASONING_EFFORT_AGENT,
                   extra_headers={'RITS_API_KEY': LLM_API_KEY_TOOLS}
                   )
    else:
        return LLM(model=f"{LLM_PROVIDER_AGENT}/{LLM_MODEL_NAME_AGENT}",
                   base_url=LLM_BASE_URL_AGENT,
                   api_key=LLM_API_KEY_AGENT,
                   api_version=LLM_API_VERSION_AGENT,
                   seed=LLM_SEED_AGENT,
                   top_p=LLM_TOP_P_AGENT,
                   temperature=LLM_TEMPERATURE_AGENT,
                   reasoning_effort=REASONING_EFFORT_AGENT
                   )

def get_llm_backend_for_tools():
    if LLM_PROVIDER_TOOLS.lower() == "rits":
        return LiteLLMBackend(provider="openai",
                              model_name=LLM_MODEL_NAME_TOOLS,
                              base_url=LLM_BASE_URL_TOOLS,
                              api_key="API_KEY",
                              api_version=LLM_API_VERSION_TOOLS,
                              seed=LLM_SEED_TOOLS,
                              top_p=LLM_TOP_P_TOOLS,
                              temperature=LLM_TEMPERATURE_TOOLS,
                              reasoning_effort=REASONING_EFFORT_TOOLS,
                              is_native_function_calling_supported=IS_NATIVE_FUNCTION_CALLING_SUPPORTED,
                              extra_headers={'RITS_API_KEY': LLM_API_KEY_TOOLS}
                              )
    else:
        return LiteLLMBackend(provider=LLM_PROVIDER_TOOLS,
                              model_name=LLM_MODEL_NAME_TOOLS,
                              base_url=LLM_BASE_URL_TOOLS,
                              api_key=LLM_API_KEY_TOOLS,
                              api_version=LLM_API_VERSION_TOOLS,
                              seed=LLM_SEED_TOOLS,
                              top_p=LLM_TOP_P_TOOLS,
                              temperature=LLM_TEMPERATURE_TOOLS,
                              reasoning_effort=REASONING_EFFORT_TOOLS,
                              is_native_function_calling_supported=IS_NATIVE_FUNCTION_CALLING_SUPPORTED
                              )
