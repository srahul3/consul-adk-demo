# Setup Consul and Nomad with TLS and Transparent Proxy
Before we start, make sure you have the following prerequisites:
- Google API Key with access to Google Gemini LLM model
- Weather API Key (visit https://www.weatherapi.com/)

```bash
# preparing secrets
touch .env
echo "GOOGLE_API_KEY=<your_google_api_key>" >> .env
echo "WEATHER_API_KEY=<your_weather_api_key>" >> .env
echo "CONSUL_HTTP_TOKEN=e95b599e-166e-7d80-08ad-aee76e7ddf19" >> .env

# aws account secrets
export AWS_ACCESS_KEY_ID=***
export AWS_SECRET_ACCESS_KEY=***
export AWS_SESSION_TOKEN=***

# creating the Nomad and Consul cluster
./apply.sh

# keep output for above command
ssh_to_client_service = <<EOT
ssh_to_client_service:
ssh -i "minion-key.pem" ubuntu@3.110.125.150
ssh -i "minion-key.pem" ubuntu@13.203.43.193

consul_ui_url
http://13.126.120.30:8500

nomad_ui_url:
http://13.126.120.30:4646

ssh_to_consul:
ssh -i "minion-key.pem" ubuntu@13.126.120.30

Use token:
e95b599e-166e-7d80-08ad-aee76e7ddf19


**Launch the CLI (cmd.py)**
python3 -m app.cmd.cmd --agent http://3.110.125.150:10002
python3 -m app.cmd.cmd --agent http://13.203.43.193:10002


EOT
```

Yay! We have successfully created a Consul and Nomad cluster with TLS and Transparent Proxy enabled.

# Uploading Python application to Nodes

```bash
./patch-ai-new.bash
```

# create consul intentions using UI
Note use Consul URL and Token from the output of `apply.sh`
```
All Services -> All Services DENY
or
consul intention create -deny '*' '*'
```

# Deploying jobs to Nomad
Note Nomad UI URL and Token from the output of `apply.sh`
```bash
In directory `./shared/nomad`, run all the jobs using Nomad UI
```

# Client CLI
```bash
# Environment setup
python3 -m venv .venv
source .venv/bin/activate
pip install .

# Running the Client CLI
python3 -m app.cmd.cmd --agent http://*.*.*.*:10002 # as mentioned in the output of `apply.sh`
```

# Testing Prompts
Try following prompts in the above CLI:
```txt
Q: How is the weather in Paris?
Agent says: I am sorry, I cannot fulfill this request. I do not have access to real-time information, such as weather forecasts.  To get the current weather in Paris, you will need to use a weather website or app.

Q: Exchange rate of USD to INR?
Agent says: I am sorry, I cannot fulfill this request. I do not have access to real-time information, such as current exchange rates.  To get the current USD to INR exchange rate, you will need to use a financial website or app that provides live currency data.
```

## Add Consul Service intentions
Add Consul intentions to allow communication between services
```bash
consul intention create -allow host-agent-app weather-agent-app
```

Try the above prompts again in same CLI:
```txt
Q: How is the weather in Paris?
Agent says: The weather in Paris is currently moderate rain, with a temperature of 20.3°C (68.5°F), 83% humidity, and a 12.3 mph wind blowing from the West.

Q: Exchange rate of USD to INR?
Agent says: I am sorry, I cannot fulfill this request. I do not have access to real-time information, such as current exchange rates.  To get the current USD to INR exchange rate, you will need to use a financial website or app that provides live currency data.
```

Add other Consul intentions to allow communication between other agent and MCPs
```bash
consul intention create -allow host-agent-app travel-agent-app
consul intention create -allow travel-agent-app currency-converter-mcp
```

Try the above prompts again in same CLI:
```txt
Q: How is the weather in Paris?
Agent says: The weather in Paris is currently moderate rain, with a temperature of 20.3°C (68.5°F), 83% humidity, and a 12.3 mph wind blowing from the West.

Q: Exchange rate of USD to INR?
Agent says: The current exchange rate for USD to INR is 86.14.  This data is from 2025-07-18. To get the current USD to INR exchange rate, you will need to use a financial website or app that provides live currency data.
```

# URLs
https://www.hashicorp.com/en/blog/using-consul-s-transparent-proxy-on-virtual-machines
https://github.com/hashicorp/nomad/issues/22432


# Sample Conversation
```bash
ubuntu@ip-172-31-22-226:~$ curl service-hello.service.consul:5050/hello

{
  "name": "hello-app",
  "uri": "/hello",
  "type": "HTTP",
  "ip_addresses": [
    "172.17.0.3"
  ],
  "start_time": "2025-07-10T05:29:39.229034",
  "end_time": "2025-07-10T05:29:44.233461",
  "duration": "5.00442667s",
  "body": "Hello from your Hello fakeservice!",
  "upstream_calls": {
    "http://response-service.virtual.consul/response": {
      "uri": "http://response-service.virtual.consul/response",
      "code": -1,
      "error": "Error communicating with upstream service: Get \"http://response-service.virtual.consul/response/hello\": dial tcp: lookup response-service.virtual.consul on 172.31.22.226:53: read udp 172.17.0.3:39953-\u003e172.31.22.226:53: read: connection refused"
    }
  },
  "code": 500
}
```




ubuntu@ip-172-31-22-226:~$ nslookup response-service.virtual.consul
Server:         127.0.0.53
Address:        127.0.0.53#53

Non-authoritative answer:
Name:   response-service.virtual.consul
Address: 240.0.0.5
# Nomad client debug

# generating certificates
```bash
cd ./7-consul-nomad-tls/shared/certs

consul tls ca create -days 1825
==> Saved consul-agent-ca.pem
==> Saved consul-agent-ca-key.pem

consul tls cert create -server -days 1825
==> WARNING: Server Certificates grants authority to become a
    server and access all state in the cluster including root keys
    and all ACL tokens. Do not distribute them to production hosts
    that are not server nodes. Store them as securely as CA keys.
==> Using consul-agent-ca.pem and consul-agent-ca-key.pem
==> Saved dc1-server-consul-0.pem
==> Saved dc1-server-consul-0-key.pem

consul tls cert create -client -days 1825
==> Using consul-agent-ca.pem and consul-agent-ca-key.pem
==> Saved dc1-client-consul-0.pem
==> Saved dc1-client-consul-0-key.pem
```

# Part 3: Consul Integration

The setup is composed of:
`api-gw->service-hello` -> 
`service-hello-proxy` -> 
`service-response-proxy` ->
`service-response`

**Run following command**
```bash
cd ./3-consul-service-mesh-simple

terraform init
terraform apply -var-file=variables.hcl
```

Copy the env section from terraform output and execute in terminal
```bash
# Sample only
export SSH_HELLO_SERVICE="ssh -i "minion-key.pem" ubuntu@<54.152.176.160>"
export SSH_RESPONSE_SERVICE_0="ssh -i "minion-key.pem" ubuntu@44.212.58.112"
export SSH_RESPONSE_SERVICE_1="ssh -i "minion-key.pem" ubuntu@3.86.29.88"

export HELLO_SERVICE=54.152.176.160
export RESPONSE_SERVICE_0=44.212.58.112
export RESPONSE_SERVICE_1=3.86.29.88
```
nomad client
```bash
ubuntu@ip-172-31-19-166:~$ ip addr show nomad
4: nomad: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default qlen 1000
link/ether fe:fe:57:b2:79:fa brd ff:ff:ff:ff:ff:ff
inet 172.26.64.1/20 brd 172.26.79.255 scope global nomad
valid_lft forever preferred_lft forever
inet6 fe80::fcfe:57ff:feb2:79fa/64 scope link
valid_lft forever preferred_lft forever
```