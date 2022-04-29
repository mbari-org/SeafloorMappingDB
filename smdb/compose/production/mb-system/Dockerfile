FROM  mbari/mbsystem:latest

# Need to create home directory before .ssh volume is mounted by production.yml
ARG DOCKER_USER_ID
RUN useradd docker_user -u $DOCKER_USER_ID -g 0
RUN echo "export LD_LIBRARY_PATH=/usr/local/lib64" >> /home/docker_user/.bashrc
RUN echo "GMT_CUSTOM_LIBS = /usr/local/lib/mbsystem.so" >> /home/docker_user/gmt.conf
# https://stackoverflow.com/a/39044217
RUN echo "LANG=en_US.UTF-8" >> /etc/environment
RUN echo "LC_ALL=en_US.UTF-8" >> /etc/environment
