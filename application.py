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

import sys

import requests

project = sys.argv[1]
pipx_data = requests.get(f"https://pypi.org/pypi/{project}/json").json()
print(pipx_data["info"]["version"])
