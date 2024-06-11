# socialmedia

Note: This project has been created for the demonstration purposes only. Please don't treat this as a production ready deployment.

# Installation Guide

Install Docker in your machine.

Clone this repository in your local drive using below command.

`git clone https://github.com/mohitey7/socialmedia.git`

Once docker is installed and above repository is cloned, open terminal in the cloned directory i.e. Dockerfile and docker-compose.yml should be at the root of the directory.

Run below command to build and run docker image in the interactive shell.

`docker compose up --build`

Or if you wish to run the container in the background, run below command.

`docker compose up --build -d`

You may see below logs if you have run container in the foreground.

```
System check identified no issues (0 silenced).
June 11, 2024 - 20:05:31
Django version 5.0.6, using settings 'socialmedia.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

If you have run in the detached mode, run below command to see the logs.
"docker logs Application"

Note: If you face any errors with `docker compose`, make sure to change the version in the `docker-compose.yml` file as per your Docker version. If you are on a Linux system, add `sudo` as a prefix before all the docker commands.

To test the endpoints, kindly import the collection file "Social Media.postman_collection" in your Postman. For API usage guide, refer to below documentation.
https://documenter.getpostman.com/view/23355221/2sA3XMiiY8
