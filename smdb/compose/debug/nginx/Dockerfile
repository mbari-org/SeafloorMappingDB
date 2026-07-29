FROM docker.io/nginx:1.13

# Set DOCKER_USER_ID in shell, e.g. export DOCKER_USER_ID=$(id -u)
ARG DOCKER_USER_ID

# Create and configure user that can read SeafloorMapping share
RUN useradd --uid $DOCKER_USER_ID docker_user 

ADD compose/debug/nginx/nginx.conf /etc/nginx/
# Remove the default welcome-page config before adding ours
RUN rm -f /etc/nginx/conf.d/default.conf
ADD compose/debug/nginx/conf.d/smdb.conf /etc/nginx/conf.d/
