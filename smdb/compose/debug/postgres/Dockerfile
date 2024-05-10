# https://github.com/postgis/docker-postgis/issues/216#issuecomment-1763399631
FROM imresamu/postgis-arm64:15-recent

COPY ./compose/production/postgres/maintenance /usr/local/bin/maintenance
RUN chmod +x /usr/local/bin/maintenance/*
RUN mv /usr/local/bin/maintenance/* /usr/local/bin \
    && rmdir /usr/local/bin/maintenance
