FROM docker.io/nginx:1.13

# Set DOCKER_USER_ID in shell, e.g. export DOCKER_USER_ID=$(id -u)
ARG DOCKER_USER_ID

# Create and configure user that can read SeafloorMapping share
RUN adduser docker_user --uid $DOCKER_USER_ID

ADD compose/production/nginx/nginx.conf /etc/nginx/
