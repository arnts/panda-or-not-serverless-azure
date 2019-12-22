A simple project to test deploying a trained models using Azure Functions.

The model is bears.pkl - an 87MB file. See the notebook in the [panda-or-not](https://github.com/arnts/panda-or-not) repository for how it is trained.

The Dockerfile means the entire thing can be deployed to Azure Functions (serverless compute).

This rest of this README serves as a quick guide / reference for how to create a deployable image and run it on Azure 

## Local Setup 

#### Requirements
- Linux (This guide has been tested with Ubuntu 16.04, xenial)
- Python 3.6 (only Python runtime currently supported by Azure Functions)
- Azure Functions Core Tools version 2.x
- Azure CLI
- Docker

#### Setup project directory

```bash
mkdir panda-or-not-serverless-azure
cd panda-or-not-serverless-azure
python -m venv .env
source .env/bin/activate
```

#### Create an Azure Function Project, and select a Python runtime
```bash
$ func init --docker
```

#### Create Function
```bash
$ func new --name panda-or-not --template "HttpTrigger"
```

#### Install dependencies
```bash
$ pip install fastai torch torchvision
$ pip freeze > requirements.txt
```

#### Update Function
Modify __init__.py and function.json (as in this project)

#### Copy model
Copy the trained model, bears.pkl, to .

#### Test function
Start the function on your local machine
```bash
$ func host start
```

Validate the function 
```bash
$ curl -X POST -H "Content-Type: application/json" -d '{"url": "https://media.pri.org/s3fs-public/styles/story_main/public/images/2019/11/2019-11-19-beibeipanda.jpg"}' http://localhost:80/api/panda-or-not
```

Output should be something like:
```bash
request_json['url']: https://media.pri.org/s3fs-public/styles/story_main/public/images/2019/11/2019-11-19-beibeipanda.jpg,pred_class: panda_bear
```

## Docker Setup

#### Build a Docker image

```bash
$ docker build -t <DOCKER_HUB_ID>/panda-or-not .
```

#### Test the Docker image

Run the Docker image on your local machine on port 8080
```bash
$ docker run -p 8080:80 -it <DOCKER_HUB_ID>/panda-or-not
```

Validate the service from another terminal window

```bash
$ url -X POST -H "Content-Type: application/json" -d '{"url": "https://media.pri.org/s3fs-public/styles/story_main/public/images/2019/11/2019-11-19-beibeipanda.jpg"}' http://localhost:8080/api/panda-or-not
```

#### Push Docker image to Docker Hub 

Log in to Docker from the command prompt
```bash
$ docker login --username <DOCKER_HUB_ID>
```

Push the Docker image created earlier to Docker Hub
```bash
$ docker push <DOCKER_HUB_ID>/panda-or-not
```

## Azure Setup

The following assumes you have a resource group named dsvmfastai.

#### Create Storage Account

```bash
$ az storage account create --name deeplearningprotostorage --location "West Europe" --resource-group dsvmfastai --sku Standard_LRS
```

#### Create a Linux App Service Plan

```bash
$ az appservice plan create --name deeplearningprotoservice --resource-group dsvmfastai --sku B1 --is-linux
```

#### Create the App & Deploy the Docker image from Docker Hub

```bash
$ az functionapp create --resource-group dsvmfastai --name pandaornot --storage-account  deeplearningprotostorage --plan deeplearningprotoservice --deployment-container-image-name arnts/panda-or-not
```

#### Configure the function app

```bash
$ storageConnectionString=$(az storage account show-connection-string --resource-group dsvmfastai --name deeplearningprotostorage --query connectionString --output tsv) 
```

```bash
$ az functionapp config appsettings set --name pandaornot --resource-group dsvmfastai --settings AzureWebJobsDashboard=$storageConnectionString AzureWebJobsStorage=$storageConnectionString
```

#### Run your Azure Function
After the previous command, it can take 15-20 minutes for the app to deploy on Azure.

```bash
$ az functionapp list --resource-group dsvmfastai
```
Validate the remote service

```bash
$ curl -X POST -H "Content-Type: application/json" -d '{"url": "https://media.pri.org/s3fs-public/styles/story_main/public/images/2019/11/2019-11-19-beibeipanda.jpg"}' https://pandaornot.azurewebsites.net/api/panda-or-not
```

Output should be

> request_json['url']: https://media.pri.org/s3fs-public/styles/story_main/public/images/2019/11/2019-11-19-beibeipanda.jpg, pred_class: panda_bear

