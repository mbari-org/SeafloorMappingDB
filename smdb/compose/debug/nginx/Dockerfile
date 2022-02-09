FROM docker.io/nginx:1.13

# Create and configure user that can read SeafloorMapping share
RUN adduser mccann --uid 399
ADD compose/debug/nginx/nginx.conf /etc/nginx/
