#!/usr/bin/env python3.11

import argparse
import io
import re
import sys
import tarfile
import tomllib

import docker

PLUGIN_METADATA = """ {
    "SchemaVersion": "0.1.0",
    "Vendor": "Fabian Lange",
    "Version": "1.0.0",
    "ShortDescription": "It's pybuild yall"
}"""

if sys.argv[1] == "docker-cli-plugin-metadata":
    print(PLUGIN_METADATA)
    sys.exit(0)

parser = argparse.ArgumentParser()
parser.add_argument("file")
parser.add_argument("--tag")
args = parser.parse_args(sys.argv[2:])


# stolen from https://packaging.python.org/en/latest/specifications/inline-script-metadata/#reference-implementation
REGEX = r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$"


def read_inline_metadata(script: str) -> dict | None:
    name = "script"
    matches = list(filter(lambda m: m.group("type") == name, re.finditer(REGEX, script)))
    if len(matches) > 1:
        raise ValueError(f"Multiple {name} blocks found")
    elif len(matches) == 1:
        content = "".join(
            line[2:] if line.startswith("# ") else line[1:]
            for line in matches[0].group("content").splitlines(keepends=True)
        )
        return tomllib.loads(content)
    else:
        return None


if __name__ == "__main__":
    print("building")
    filename = args.file
    with open(filename) as f:
        content = f.read()
    metadata = read_inline_metadata(content)
    dockerfile_content = metadata["tool"]["docker"]["Dockerfile"]
    dockerfile_content = "\n".join([line.strip() for line in dockerfile_content.splitlines()])
    print(dockerfile_content)

    dockerfile = io.BytesIO(dockerfile_content.encode())
    client = docker.from_env()
    tar_buffer = io.BytesIO()

    with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
        tar.add(filename, arcname=filename)
        dockerfile_info = tarfile.TarInfo(name="Dockerfile")
        dockerfile_info.size = len(dockerfile_content)
        tar.addfile(dockerfile_info, dockerfile)

    tar_buffer.seek(0)

    tag = args.tag or "pybuild-example"
    client.images.build(fileobj=tar_buffer, custom_context=True, tag=tag)

    print(f'Finished building {tag}, you can now run "docker run {tag} <package name>"')
