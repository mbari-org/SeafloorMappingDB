FROM docker.io/nginx:1.13

# Set DOCKER_USER_ID in shell, e.g. export DOCKER_USER_ID=$(id -u)
ARG DOCKER_USER_ID

# Create and configure user that can read SeafloorMapping share
RUN useradd --uid $DOCKER_USER_ID docker_user 

ADD compose/debug/nginx/nginx.conf /etc/nginx/
