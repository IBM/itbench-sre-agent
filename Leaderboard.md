## Prerequisites:  
1. Podman (or Docker)
2. Install ibmcloud cli using directions below
   
For Mac user:
```bash
curl -fsSL https://clis.cloud.ibm.com/install/osx | sh
```

For Linux user:
```bash 
curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
```  
  
Login to the ibmcloud cli
```bash 
ibmcloud login --sso
```
  
Choose the RIS3 account  
  
Login to the cloud registry
```bash
ibmcloud cr login
```

Register a user in [the UI](https://itbench.apps.staging.itbench.res.ibm.com/top) and login  
  
## Instructions:  
1. Clone the repo and checkout the branch `main-no-agent-sdk`  
```bash
git clone git@github.ibm.com:DistributedCloudResearch/lumyn.git  
cd lumyn  
git checkout main-no-agent-sdk
```  
  
2. Update environment variables  
```bash
cp .env.tmpl .env  
vi .env
```  
  
3. Pull the base image  
```bash
podman pull icr.io/agent-bench/agent-harness:latest
```  
  
4. Build sre-agent-harness image  
```bash
podman build . -f sre-agent-harness.Dockerfile -t sre-agent-harness:latest
```


5. Connect to IBM TUNNELALL VPN by copying [sasvpn-dc.us.ibm.com/macOS-TUNNELALL](sasvpn-dc.us.ibm.com/macOS-TUNNELALL) into your Cisco Secure Client
  
6. Run the image in interactive mode  
```bash
podman run --rm -it --name sre-agent-harness sre-agent-harness:latest bash
```  
  
7. Register the agent in the [the UI](https://itbench.apps.staging.itbench.res.ibm.com/top) and copy the ID and Token for the next step  
  
8. Update env variables by running  
```bash
export AUTO_BENCH_BENCH_SERVER_HOST=itbench.apps.staging.itbench.res.ibm.com
export AUTO_BENCH_BENCH_SERVER_PORT=0
export AUTO_BENCH_AGENT_ID=<get from the UI>
export AUTO_BENCH_AGENT_TOKEN=<get from the UI>
export AUTO_BENCH_AGENT_DIR=/app/lumyn
export AUTO_BENCH_BENCHMARK_TIMEOUT=3600
```  
  
9. Run the harness  
```bash
/app/agent-benchmark/agent_bench_automation/agent_harness/sre_agent_harness/entrypoint.sh "$AUTO_BENCH_BENCH_SERVER_HOST" "$AUTO_BENCH_BENCH_SERVER_PORT" "$AUTO_BENCH_AGENT_ID" "$AUTO_BENCH_AGENT_TOKEN" "$AUTO_BENCH_AGENT_DIR" "$AUTO_BENCH_BENCHMARK_TIMEOUT"
``` 
  
10. Create the benchmark in [the UI](https://itbench.apps.staging.itbench.res.ibm.com/top)  
