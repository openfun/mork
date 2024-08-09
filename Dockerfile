# -- Base image --
FROM python:3.12-slim AS base

# Upgrade pip to its latest release to speed up dependencies installation
RUN pip install --upgrade pip

# Upgrade system packages to install security updates
RUN apt-get update && \
    apt-get -y upgrade && \
    rm -rf /var/lib/apt/lists/*

# -- Builder --
FROM base AS builder

WORKDIR /build

# Copy required python dependencies
COPY ./src/app /build

RUN mkdir /install && \
    pip install --prefix=/install .

# ---- mails ----
FROM node:20 AS mail-builder

COPY ./src/mail /mail/app

WORKDIR /mail/app

RUN yarn install --frozen-lockfile && \
    yarn build
        
# -- Core --
FROM base AS core

# Copy installed python dependencies
COPY --from=builder /install /usr/local

# Copy mork application (see .dockerignore)
COPY ./src/app /app/

WORKDIR /app


# -- Development --
FROM core AS development

# Switch to privileged user to uninstall app
USER root:root

# Uninstall mork and re-install it in editable mode along with development
# dependencies
RUN pip uninstall -y mork-ork
RUN pip install -e .[dev]

# Un-privileged user running the application
ARG DOCKER_USER=1000
USER ${DOCKER_USER}


# -- Production --
FROM core AS production

# Un-privileged user running the application
ARG DOCKER_USER=1000
USER ${DOCKER_USER}

# Copy mork mails
COPY --from=mail-builder /mail/app/mork/templates /app/src/app/mork/templates

CMD ["uvicorn", \
     "mork.api:app", \
     "--proxy-headers", \
     "--log-config", \
     "logging-config.prod.yaml", \
     "--host", \
     "0.0.0.0", \
     "--port", \
     "8100"]
