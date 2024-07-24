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

COPY . /build/

RUN pip install .


# -- Core --
FROM base AS core

COPY --from=builder /usr/local /usr/local

WORKDIR /app


# -- Development --
FROM core AS development

# Copy all sources, not only runtime-required files
COPY . /app/


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

CMD ["uvicorn", \
     "mork.api:app", \
     "--proxy-headers", \
     "--log-config", \
     "logging-config.prod.yaml", \
     "--host", \
     "0.0.0.0", \
     "--port", \
     "8100"]
