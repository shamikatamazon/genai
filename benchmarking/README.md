# A script to benchmark model performance 

Before deploying models to production, we need to understand the latency and throughput of an LLM to accurately deploy infrastructure to support traffic patterns. Given the expense and paucity of GPUs, its important we are able to squeeze out every bit of performance from our GPUs and ensure instances are right-sized to minimize GPU idle time. The scripts below provide a simple way to quickly test and approximate the performance of a model. 


## Using vLLM to deploy a model 

vLLM (https://github.com/vllm-project/vllm) is a fast and easy-to-use library for LLM inference and serving and provides an easy way to quickly deploy a model on an instance. For my tests, I've used a g5.12xl EC2 instance with the Deep Learning Ubuntu AMI (https://docs.aws.amazon.com/dlami/latest/devguide/what-is-dlami.html) as it comes pre-installed with a bunch of utilities and drivers required for inferencing.

Instantiate and deploy your instance and `ssh` into it and then install `vLLM` by running the command `pip install vLLM`, detailed instructions can be found at https://docs.vllm.ai/en/latest/getting_started/installation.html

vLLM can deploy a model and provide a OpenAPI compatible API to access the model. (https://docs.vllm.ai/en/latest/getting_started/quickstart.html#openai-compatible-server). We use this to start our server and deploy a model 

`python -m vllm.entrypoints.openai.api_server --model mistralai/Mistral-7B-Instruct-v0.1`

This will deploy Mistral-7B with tensor-parallelism=1 (default option), since we are using a g5.12xl, which has 4 GPU cores, you can set the tp value to 4 to maximize throughput

`python -m vllm.entrypoints.openai.api_server --model mistralai/Mistral-7B-Instruct-v0.1 -tp 4`

vLLM will download the model, deploy it and instanstiate a webserver to serve inference requests. This process will take some time and the model is ready for infernce when you see the message below.

```INFO:     Started server process [40118]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Setting up Prometheus and Grafana for scapring and graphing metrics 

You can choose to run Prometheus and Grafana on the same g5.12xl thats being used for inference or you can spin up another EC2 instance for Prometheus and Grafana, I prefer having another instance as there is a clear serperation between the instances being used for inference and reporting, however if cost is a primary consideration, feel free to use the same instance. 

Log into the system and install Prometheus and Grafana, the instructions are available at https://prometheus.io/docs/prometheus/latest/installation/ for Prometheus and https://grafana.com/docs/grafana/latest/setup-grafana/installation/ for Grafana


### Install Prometheus
I installed using Prometheus by first downloading the Prometheus binary from the prometheus github page and extacting the zip archive

```
wget https://github.com/prometheus/prometheus/releases/download/v2.45.2/prometheus-2.45.2.linux-amd64.tar.gz
tar -xvf prometheus-2.45.2.linux-amd64.tar.gz
```

Once installed, edit the prometheus.yaml file to configure the targets that need to be scraped. Open the prometheus.yml file and search for the scrape_configs section and update the targets section to point to the IP of the instance that hosts vLLM. 

```
scrape_configs:
  # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
  - job_name: "prometheus"

    # metrics_path defaults to '/metrics'
    # scheme defaults to 'http'.

    static_configs:
      - targets: ["<IP of EC2 Instance that hosts vLLM>:8000"]
```

Once updated, start prometheus by using the command

```
./prometheus --config.file=./prometheus.yml 
```

In order for Prometheus to scrape the metrics from vLLM, the Security Groups of the EC2 instance hosting vLLM needs to be updated to open the ports that exposes the metrics.

### Install Grafana

Install Grafana by using yum package manager 

```
sudo yum install -y https://dl.grafana.com/enterprise/release/grafana-enterprise-10.2.3-1.x86_64.rpm
```

Once installed, start Grafana 

```
sudo systemctl start grafana-server
```

:warning: Grafana runs on port 3000 and the security group of the EC2 instance needs to be updated to open port 3000. 

Once the Security group is updated, using your browser open https://<IP of the EC2 instance>:3000/

You will see the welcome Grafana screen and will be able to create an admin user and provide a admin password the first time you login. 



## Generating load for peforming an inference 

Copy the the [python script](benchmarkWithvLLM.py) on any of the EC2 instances that you have already spun up or on a new instance. 

install the dependencies required for the python script 

```
pip install prometheus_client requests
```

Update the location of your vLLM deployment in your script by editing this line in the code

```
url = 'http://ec2-3-88-200-227.compute-1.amazonaws.com:8000/v1/completions'
```

and configure your "scrape" port by editing this line 

```
start_http_server(<port_number>, registry=registry)
```

:warning: Ensure that the Security Groups for the EC2 instance that is used to run this script has been updated to open the configured port. 


Create a temporary directory and set the ```PROMETHEUS_MULTIPROC_DIR``` to point to it 

```
mkdir tmp
export PROMETHEUS_MULTIPROC_DIR=<full path to tmp directory>
```


Run the python script 

```
python benchmarkWithvLLM.py
```

The script will create 20 processes and hit the model with the inference requests and expose the metrics until the python process is killed. 

The number of concurrent processes can be changed by editting this line in the code 

```
for i in range(1,<number of processes>):
```

Once the code starts to execute, the following metrics are tracked and reported to prometheus 

```
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
PROMPT_TOKEN_COUNTER = Counter('prompt_token_counter', 'tokens in prompt')
GENERATED_TOKEN_COUNTER = Counter('generated_token_counter', 'tokens generated by LLM')
REQUESTS_COUNTER = Counter('enduser_requests_counter', 'tokens generated by LLM')
```


## Viewing metrics in Grafana

Log into the Grafana by going to the ```http://<IP of EC2 hosting model>:3000``` 

Click on the 3 horizontal line button on the top left and click on ```Connections``` and ```Add New Connection```

Choose ```Prometheus``` and enter the location of the prometheus deployment

Once the data source is created, Click the 3 horizontal line button and choose Dashboards and on the next screen, click the New Button and select ```Import```

On the import Dashboard screen, in the text box below ```Import via dashboard JSON model``` copy paste the contents of the [Grafana Dashboard json](grafanaDashboard.json)

Once the dashboard loads, you will see data in the ```vLLM Generated Metrics``` section on the bottom half of the screen. 


## Viewing metrics generated by the Python inferencing client 

Log back into the EC2 instance hosting prometheus and edit the prometheus.conf file to scrape metrics generated by the python script. 

```
- job_name: "python_request"
    static_configs:
      - targets: ["<IP of EC2 instance>:9000"]
```

Restart prometheus to load the new config and go to the Grafana dashboard, you will see all the graphs in the dashboard reporting metrics. 

## Benchmarking a model deployed with hugging-face pipelines

The [script](benchmark_hf_model.py) is an example of deploying a model using huggingface pipelines and benchmarking performance. A model is deployed using pipelines, and then inference is performed on the model, where inference time and input/output tokens are calculated and reported to prometheus. Grafana is then used for building dashboards to view the metrics. 

Use the same instructions as ```Viewing metrics in Grafana``` section to deploy the dashboard, except swap out the [Grafana Dashboard json](grafanaDashboard.json) with [Grafana Dashboard Huggingface json](grafanaDashboard_hf.json)