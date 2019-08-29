import os
import subprocess
from pathlib import Path
from typing import Dict, Optional

import requests
import yaml
from requests.exceptions import HTTPError


def credentials_exist() -> bool:
    return 'DOCKER_USERNAME' in os.environ and 'DOCKER_PASSWORD' in os.environ


def assert_credentials_exist():
    if not credentials_exist():
        raise RuntimeError(
            'Error: environment variables $DOCKER_USERNAME and $DOCKER_PASSWORD are not set.')


def get_docker_token() -> str:
    """Get a token for docker hub."""

    headers = {
        'Content-Type': 'application/json',
    }
    data = f'''{{"username": "{os.environ['DOCKER_USERNAME']}", "password": "{os.environ['DOCKER_PASSWORD']}"}}'''
    response = requests.get(
        'https://hub.docker.com/v2/users/login/', headers=headers, data=data)
    response.raise_for_status()
    token = yaml.safe_load(response.text)['token']
    return token


def docker_image_exists(image_id: str) -> bool:
    """Check if a docker image with the given image_id exists on ducker hub using v2 of the docker hub api."""

    if ':' not in image_id:
        raise ValueError(
            f'Invalid image_id specified: {image_id}. A image_id should be of the format: "{{name}}:{{tag}}"')
    name, tag = image_id.split(':')
    token = get_docker_token()
    headers = {
        'Authorization': f'JWT {token}'
    }
    response = requests.get(
        f'https://hub.docker.com/v2/repositories/{name}/tags/', headers=headers)
    if response.status_code == 404:
        return False
    response.raise_for_status()
    text = yaml.safe_load(response.text)
    tags = [r['name'] for r in text['results']]

    return tag in tags


def docker_build(image_id: str, dir_path: Path, build_args: Optional[Dict[str, str]] = None):
    """Builds a docker image.

    Tries to build using the cache first. If that fails, then it tries again without the cache."""

    if build_args:
        build_args_string = ' '.join(
            f'--build-arg {k}={v}' for k, v in build_args.items())
    else:
        build_args_string = ''
    try:
        subprocess.run(
            f'docker build -t {image_id} {build_args_string} {dir_path}', shell=True, check=True)
    except:
        subprocess.run(
            f'docker build -t {image_id} --no-cache {build_args_string} {dir_path}', shell=True, check=True)


def docker_push(image_id: str):
    subprocess.run(
        f'echo "$DOCKER_PASSWORD" | docker login --username $DOCKER_USERNAME --password-stdin; docker push {image_id}', shell=True, check=True)


def build(image_id: str, dir_path: Path, build_args: Optional[Dict[str, str]] = None):
    """Builds and pushes the appropriate docker image."""

    assert_credentials_exist()
    if not docker_image_exists(image_id):
        docker_build(image_id, dir_path, build_args)
        docker_push(image_id)
        assert docker_image_exists(
            image_id), 'The docker image was just built and pushed without error, but does not appear to exist.'
