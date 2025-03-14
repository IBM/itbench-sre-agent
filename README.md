# Setup a remote or local cluster to run the ITBench
Clone and follow the instructions in [this repo](https://github.com/IBM/it-bench-sample-scenarios/tree/main/sre). Setup a cluster, deploy the observability stack and a sample application, then inject a fault.

# Running with Docker/Podman
The agent should always be run in a container in order to prevent harmful commands being run on the user's PC.  

1. Clone the repo
```
git clone git@github.com:IBM/itbench-sre-agent.git
cd itbench-sre-agent
```

2. Create a `.env` based on `.env.tmpl` by running:
```
cp .env.tmpl .env
```
Update the values here to switch LLM backends. Supports all providers and models that are available through [LiteLLM](https://docs.litellm.ai/docs/providers). Also update the values at the bottom so the agent can interact with your cluster.

3. Build the image.
```
# Docker
docker build -t itbench-sre-agent .
# Podman
podman build -t itbench-sre-agent .
```

4. Run the image in interactive mode:
```
# Docker
docker run -it itbench-sre-agent /bin/bash
# Podman
podman run -it itbench-sre-agent /bin/bash

# FOR LINUX ONLY
If you are running the agent on the same machine as the bench then you need to run portforwarding on the bench (kubectl port-forward svc/ingress-nginx-controller -n ingress-nginx 8080:80)
and then run the agent image with --network=host (docker run --network=host -it itbench-sre-agent /bin/bash) and then for the grafana url use http://localhost:8080/prometheus.
```
5. Start the agent:
```
sudo crewai run
```

Pre-built images coming soon.

# Development Setup Instructions
1. Clone the repo
```
git clone git@github.com:IBM/itbench-sre-agent.git
cd itbench-sre-agent
```

2. This project uses Python 3.12. Install uv for dependecy management, and install crewai.
Mac/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install crewai
```
  
Windows  
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv tool install crewai
```
3. Navigate to the root project directory and install the dependencies using the CLI command:
```
crewai install
```
  
4. Create a `.env` based on `.env.tmpl` by running:
```
cp .env.tmpl .env
```
Update the values here to switch LLM backends.
  
5. Customize:  
- Modify `src/lumyn/config/agents.yaml` to define your agents
- Modify `src/lumyn/config/tasks.yaml` to define your tasks
- Modify `src/lumyn/crew.py` to add your own logic, tools and specific args
- Modify `src/lumyn/main.py` to add custom inputs for your agents and tasks

# User Interface
To leverage Panel as a UI, head over to the ui directory (via cd ui) and run:

`panel serve panel_main.py --show`

and then head over to http://localhost:5006/panel_main in your browser. Tested in Firefox and Chrome.

To leverage Streamlit as a UI, head over to the ui directory (via cd ui) and run:

`streamlit run streamlit_main.py`

and then head over to http://localhost:5006/panel_main in your browser. Tested in Firefox and Chrome.
