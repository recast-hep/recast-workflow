import os

import pytest

import definitions
import subprocess
from images import build_utils


class TestCredentialsExist:
    def test_exists(self):
        os.environ['DOCKER_USERNAME'] = 'username'
        os.environ['DOCKER_PASSWORD'] = 'password'
        assert build_utils.credentials_exist()

    def test_does_not_exist(self):
        if 'DOCKER_USERNAME' in os.environ:
            del os.environ['DOCKER_USERNAME']
        if 'DOCKER_PASSWORD' in os.environ:
            del os.environ['DOCKER_PASSWORD']
        assert not build_utils.credentials_exist()


class TestDockerImageExists:
    def test_exists(self):
        assert build_utils.docker_image_exists('recast/madgraph:2.6.6')

    def test_version_does_not_exist(self):
        assert not build_utils.docker_image_exists('recast/madgraph:fake')

    def test_repo_does_not_exist(self):
        assert not build_utils.docker_image_exists('fake:fake')

class TestDockerBuild:
    def test_no_tag(self):
        with pytest.raises(subprocess.CalledProcessError):
            build_utils.docker_build('', os.path.join(
                definitions.ROOT_DIR, 'images', 'madgraph_pythia', 'madgraph'), None)

    def test_no_dir(self):
        with pytest.raises(subprocess.CalledProcessError):
            build_utils.docker_build(None, '', None)
    
    def test_valid(self):
        build_utils.docker_build('recast/madgraph:2.6.6', os.path.join(definitions.ROOT_DIR, 'images', 'madgraph_pythia', 'madgraph'), {'MADGRAPH_VERSION': '2.6.6'})

class TestBuild:
    def test_valid(self):
        build_utils.build('recast/madgraph:2.6.6', os.path.join(definitions.ROOT_DIR, 'images', 'madgraph_pythia', 'madgraph'), {'MADGRAPH_VERSION': '2.6.6'})