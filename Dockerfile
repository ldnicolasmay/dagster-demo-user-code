FROM python:3.10-slim

# Upgrade OS/packages
RUN apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set ENV VARS & make directories \
ENV DAGSTER_APP=/opt/dagster
ENV USER_CODE=$DAGSTER_APP/app
RUN mkdir -p $USER_CODE

# Install Python dependencies
WORKDIR $DAGSTER_APP
COPY pyproject.toml pyproject.toml
RUN pip install --upgrade pip && \
    pip install -e '.'

# Set working directory & copy user code
WORKDIR $USER_CODE
COPY . ${USER_CODE}
