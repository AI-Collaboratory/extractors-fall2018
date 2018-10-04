FROM clowder/pyclowder:2
MAINTAINER Sandeep Satheesan <sandeeps@illinois.edu>

# Setup software dependencies
USER root
COPY bintray.key /tmp/
RUN apt-key add /tmp/bintray.key
RUN echo "deb http://dl.bintray.com/siegfried/debian wheezy main" | tee -a /etc/apt/sources.list
RUN apt-get update && apt-get install -y netcat  siegfried && apt-get clean && rm -rf /var/lib/apt/lists/*
# Setup environment variables. These are passed into the container. You can change
# these to your setup. If RABBITMQ_URI is not set, it will try and use the rabbitmq
# server that is linked into the container. MAIN_SCRIPT is set to the script to be
# executed by entrypoint.sh

ENV RABBITMQ_URI="" \
    RABBITMQ_EXCHANGE="clowder" \
    RABBITMQ_VHOST="%2F" \
    RABBITMQ_QUEUE="siegfried" \
    MAIN_SCRIPT="siegfried.py"

# Switch to clowder, copy files and be ready to run
# USER clowder

# command to run when starting docker
COPY entrypoint.sh siegfried.py extractor_info.json /home/clowder/
ENTRYPOINT ["/home/clowder/entrypoint.sh"]
CMD ["extractor"]
