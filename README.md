# Siegfried Format Identification Extractor

This repository contains a Brown Dog extractor that uses the [Siegfried](http://www.itforarchivists.com/siegfried) format identification tool to identify file formats, based on matches against the [PRONOM](https://www.nationalarchives.gov.uk/PRONOM/Default.aspx) format registry. You can clone this repository to your local system and build it right away to add it to a running Clowder or Brown Dog environment. You can also use the Docker "pull" command to download a pre-built version of this extractor from DockerHub:

    $ docker pull clowder/extractors-siegfried

# Brown Dog Runtime Environment

The Brown Dog environment includes several services that work together to deliver the Brown Dog API.
These include the Clowder web application, which hosts the API, a RabbitMQ message broker and extractor tools running on separate hosts.
Brown Dog extractors are message-based network services that process data files in response to RabbitMQ messages.
The client-facing Brown Dog API receives data from a client and passes messages to the extractor message topic.
Any extractors that are subscribed to the topic will receive the message and decide for themselves if they can process the data,
usually by looking at the MIME type. When an extractor starts or finishes working on a file it posts status and results back onto a message queue.
All communication between the Brown Dog servers and the extractor tools is handled by messaging.

# Step-by-Step Instructions

Following these instructions you should be able to install and run the Siegfried extractor, run tests using the sample files,
and even develop your own extractor program based on this one.

## Setup the Project

There are some basic software dependencies to install, after which Docker will handle the rest. Docker Compose is run from within a python virtual environment for your project. Docker Compose will start and connect several Docker containers together to create an extractor runtime environment. It will also deploy the project code into a Docker container that is connected to this runtime environment.

1. Install prerequisite software. The install methods will depend on your operating system:
 - VirtualBox (or an equivalent Docker-compatible virtualization environment)
 - Docker
 - Python and PIP
 - Git

1. Clone this extractor project from the repository:

<!-- language: bash -->
    $ git clone https://opensource.ncsa.illinois.edu/bitbucket/scm/cats/extractors-siegfried.git
    $ cd extractors-siegfried

## Create Extractor Runtime Environment
- Install Docker Compose

<!-- language: bash -->
    $ pip install docker-compose

- Start up the extractor runtime environment using Docker Compose. This starts docker containers for Clowder, MongoDB, and RabbitMQ:
<!-- language: bash -->
    $ docker-compose up -d

- Create a Clowder Account
 - Point your browser to http://localhost:9000.
 - Sign up for an account by entering an email address. (Write this down)
 - View the logs for the Clowder container to get registration link:
 ```
$ docker logs bdextractortemplate_clowder_1
```
 - Find the Clowder registration link in the log output. Point your browser at that link to complete registration, choosing a password.
 - NOTE: User registrations are persisted inside of the MongoDB container. They will remain as long as that container is not replaced with a new one.
- Find the IP of the Clowder container and note this for later:
```
$ docker exec bdextractortemplate_clowder_1 ip -d addr | grep inet
```
Find the IP address of your clowder container, ignoring the "loopback" address, which is normally 127.0.0.1.

## Build and Start the Extractor

1. Issue a Docker build command from the project folder:
```
$ docker build -t extractors-siegfried .
```
This command will take longer the first time, as all dependencies are downloaded and installed into the container. You can run the command again and it will only perform the steps in the Dockerfile that have changed.

1. Run the Extractor:
```
$ docker run --rm -i -t --link bdextractorssiegfried_rabbitmq_1:rabbitmq extractors-siegfried
```
This command starts your extractor container and links it to the RabbitMQ container's shared ports.

1. You should now have a Clowder environment with a Siegfried extractor attached.
