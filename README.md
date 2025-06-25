# docker-pybuild: Including Dockerfiles in Python inline metadata

A Docker CLI plugin that allows you to build Docker images directly from Python scripts with embedded Dockerfiles.

**Note:** This is more of a proof-of-concept than a fully developed plugin.

## Motivation

[PEP-723](https://peps.python.org/pep-0723/) made some waves recently as it allows you to specify the required Python version
as well as packages that are required by a script.

Since I mostly use Python with Docker, I was wondering if there is an easy way to specify the whole Dockerfile
as part of the inline metadata. I created this plugin because I don't use tools like `uv` or `pipx` on my host system,
preferring to run Python applications in containers instead.

So here it is, a way to build a standalone script into a Docker image without requiring any Python package management
tools on your host system.

## Installation

As a Docker CLI plugin, you need to:

1. Make the script executable: `chmod +x docker-pybuild.py`
2. Place it in your Docker CLI plugins directory (or symlink it):
   ```
   ln -s $(pwd)/docker-pybuild.py ~/.docker/cli-plugins/docker-pybuild
   ```

## Usage

1. Create a Python script with inline Dockerfile metadata:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests<3"
# ]
# [tool.docker]
# Dockerfile = """
#   FROM python:3.11
#   RUN pip install pipx  # pip doesn't support PEP-723 yet, so we'll use pipx for now
#   WORKDIR /app
#   COPY application.py /app
#   ENTRYPOINT ["pipx", "run", "/app/application.py"]
# """
# ///

# Your Python code here
```

2. Build a Docker image from your script:
```
docker pybuild your_script.py --tag your-image-name
```

3. Run your containerized application:
```
docker run your-image-name [arguments]
```

See the included `application.py` for a complete example.
