# DAB User Management Service

This is the user management microservice which will manage the Authentication and Authorization for all other services.

## Installation
***
### Requirements:
Below software programs are required to start:

* Python > 3.x `v3.10.4 has been used in this project`
* Poetry `For package management`
* Uvicorn `ASGI Server for running the application`

### Poetry Installation:
`Windows Installation`
For installing it in Windows run the below command in PowerShell

```
(Invoke-WebRequest -Ur


i https://install.python-poetry.org -UseBasicParsing).Content | python -
```

`Linux/Mac Installation` For installing it in Linux run the following command in shell

```
curl -sSL https://install.python-poetry.org | python3 -
```


If you wanted to create a virtual environment you can do it by running this command `python -m venv .venv`

### Starting Application

First you have to install the dependencies using `poetry install`
After installing the dependencies you can run the service by issuing the command 

```uvicorn app.main:app --port 8001 --reload``` 

Once the server is running navigate to `http://localhost:8001` and check the service is running. 

FastAPI also has a documentation system which can be accessed via

`http://localhost:8001/docs/` or `http://localhost:8001/redocs/`
