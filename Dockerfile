FROM python:3.12-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


# Manually install uv
# # The installer requires curl (and certificates) to download the release archive
# RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# # Download the latest installer
# ADD https://astral.sh/uv/install.sh /uv-installer.sh

# # Run the installer then remove it
# RUN sh /uv-installer.sh && rm /uv-installer.sh

# # Ensure the installed binary is on the `PATH`
# ENV PATH="/root/.local/bin/:$PATH"

# Copy the project into the image
COPY . /app

# Disable development dependencies
ENV UV_NO_DEV=1

# Setup GDAL
RUN apt-get update && \
    apt-get install -y binutils libproj-dev gdal-bin python3-gdal && \
    rm -rf /var/lib/apt/lists/*


# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app
RUN uv sync --locked


CMD [ "sh", "./entrypoint.sh"]
