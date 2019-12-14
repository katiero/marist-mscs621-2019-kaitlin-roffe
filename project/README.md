# Python Web application for Hybrid Cloud Computing
This repository was created for the final project for the *Marist Cloud Computing* class of Fall 2019. The repository stores the files that make up the 'Gift Record' application. The purpose of the application is to record gift received and whether a thank you note cooresponding to the gift has been sent out.

The project code is written in Python and utilizes [Flask microframework](http://flask.pocoo.org/).The app is built on a [Redis](https://redis.io) database for storing JSON objects. 

Follow the steps below to get the project code and deploy it using docker or a hybrid cloud setup.

## Get the project code
Navigate to a location where you want this application code to be downloaded to and issue:
Fork https://github.com/katiero/marist-mscs621-2019-katie-roffe.git into <your account>
```bash
    $ git clone https://github.com/<your account>/project.git
```    
    
## Deploy Locally
This project can be deployed locally using Docker. Install [Docker CE (Community Edition)](https://docs.docker.com/install/linux/docker-ce/ubuntu/) and [Docker Compose (Container Orchestrator)](https://docs.docker.com/compose/install/).

Run the project code as containers using the Terminal.

```bash
    $ cd project
    $ docker-compose build
    $ docker-compose up -d
```
The application should be accessible from http://localhost:5000/ in your browser. 

The following commands can be used to remove the containers if needed:
```bash
    $ docker-compose kill
    $ docker-compose rm
```
## Deploy to Hybrid Cloud Environment
### Database
This application is designed to use a Redis database. The code was tested using Redis Enterprise to host the database. Follow the below steps to create and connect to a database hosted on Redis Enterprise.

#### Step 1:
Create database. Make sure to enable Redis Password within Access Control & Security. Take note of the endpoint associated to your database.

#### Step 2: 
Edit the models.py file. Find the section titled Redis Database Connection Methods and the section for Redis Enterprise Cloud within it. Update the hostname & port (as seen in your endpoint), and password, with the information from your Redis database.

### Application
Deployment of this application was tested using IBM Cloud (previously known as Bluemix). Follow the below steps to deploy to IBM Cloud. 

#### Step 1: 
From the terminal log into IBM Cloud and set the api endpoint to the IBM Cloud region you wish to deploy to:
```script
cf login -a api.ng.bluemix.net
```

The login will ask you for you `email`(username) and `password`, plus the `organisation` and `space` if there is more than one to choose from.


#### Step 2, Option 1:
By default the `route` (application URL) will be based on your application name. Edit the `manifest.yml` file and change the name of the application to something unique.

From the root directory of the application code execute the following:
```script
cf push <YOUR_APP_NAME> -m 64M
```

#### Step 2, Option 2:
If your application name is not unique, that is okay. The app can be deployed using a different hostname.

From the root directory of the application code execute the following:
```script
cf push <YOUR_APP_NAME> -m 64M -n <YOUR_HOST_NAME>
```

## View App
Once the application is deployed and started open a web browser and point to the application route defined at the end of the `cf push` command i.e. http://mscs621-bluemix-xx.mybluemix.net/. This will execute the code under the `/` app route defined in the `server.py` file. Navigate to `/data` to see a list of data returned as JSON objects.

## Structure of application
**Procfile** - Contains the command to run when you application starts on Bluemix. It is represented in the form `web: <command>` where `<command>` in this sample case is to run the `py` command and passing in the the `server.py` script.

**requirements.txt** - Contains the external python packages that are required by the application. These will be downloaded from the [python package index](https://pypi.python.org/pypi/) and installed via the python package installer (pip) during the buildpack's compile stage when you execute the cf push command. In this case we wish to download the [Flask package](https://pypi.python.org/pypi/Flask) at version 0.12 and [Redis package](https://pypi.python.org/pypi/Redis) at version greater than or equal to 2.10

**runtime.txt** - Controls which python runtime to use. In this case we want to use 2.7.15.

**README.md** - this readme.

**manifest.yml** - Controls how the app will be deployed in Bluemix and specifies memory and other services like Redis that are needed to be bound to it.

**server.py** - Commands to read and write to the database.

**server.py** - the python application script. This is implemented as a simple [Flask](http://flask.pocoo.org/) application. The routes are defined in the application using the @app.route() calls. This application has a `/` route and a `/data` route defined. The application deployed to Bluemix needs to listen to the port defined by the VCAP_APP_PORT environment variable as seen here:
```python
port = os.getenv('VCAP_APP_PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
```

This is the port given to your application so that http requests can be routed to it. If the property is not defined then it falls back to port 5000 allowing you to run this sample application locally.
