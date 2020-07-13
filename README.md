 
# Insumos-medicos-api-python

![Arq-Soft-Equipo3](https://circleci.com/gh/Arq-Soft-Equipo3/insumos-medicos-api-python.svg?style=svg)

This project contains source code and supporting files for a serverless application based on Amazon AWS Lambda.

## Requirements
_note: the instructions or commands are for linux based OS's. For Windows installation instructions check each provider site. Although using this may present trouble on Windows's based systems due to Docker compatibility issues_ 

For this project we'll need these tools:

- [NodeJS](https://nodejs.org/en/) (required for the serverless framework).
- [Python 3.6](https://www.python.org/downloads/) (required for the development). 
- Serverless framework (required for the deployment).
- [Docker](https://www.docker.com/products/docker-desktop) (required for the virtual environment).
- A code editor or an IDE ([VSCode](https://code.visualstudio.com/Download), Pycharm, etc).
- [GIT](https://git-scm.com/downloads) (required for versioning)
- An [AWS Lambda account](https://aws.amazon.com/es/lambda/) (for the deployment stage)


### Serverless framework
Execute this command to install the serverless framework and the python plugin for managing the python deployment

```bash
$ npm install --save-dev serverless-wsgi serverless-python-requirements
```

### Python requirements
For this project we'll need python 3.6 and the pip3 package installer.

## Setting up

After cloning this repository. Move to the project folder. Open a terminal an execute

```bash
$ virtualenv venv --python=python3
$ source venv/bin/activate
```

this will create an isolated python environment for installing the dependencies needed by our project.
now, we need to install the python dependencies needed by running in our virtual environment

```bash
(venv) $ pip install flask
(venv) $ pip install boto3
```
In order to keep the environment consistent, it’s a good idea to “freeze” the current state of the environment packages. To do this, run:

    $ pip freeze > requirements.txt
   
   ## Deployment
   Now we have two forms of deployment: local and remote (or production)

### Local

For this, we'll use the DynamoDB emulator plugin. intall the plugin with:

```
$ npm install --save-dev serverless-dynamodb-local
```

Then, run a command to install DynamoDB local:

```bash
$ sls dynamodb install
```
now we'll need to different terminals. the first one for starting up dynamo by running:

```bash
$ sls dynamodb start
```

Dynamo will start in the port 8000

The second terminal for starting the wsgi server locally

```bash
$ sls wsgi serve
```

Now we can start testing the endpoints using our browser or an API client like [Postman](https://www.postman.com/downloads/)

### Remote

first we are going to need to create and configure the AWS credentials.

 - Log in into the AWS console
 - Create a new user with administrator permission

Deploying the function on AWS lambda is as simple as running: 

```bash
$ sls deploy
```
