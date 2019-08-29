#!/usr/bin/env bash
RIVET_VERSION=${1:-latest}
echo $RIVET_VERSION
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TAG="recast/rivet:$RIVET_VERSION"

echo "$DOCKER_PASSWORD" | docker login --username $DOCKER_USERNAME --password-stdin
echo "RIVET_VERSION is ${RIVET_VERSION}"
docker build -t $TAG --build-arg RIVET_VERSION=$RIVET_VERSION $DIR
docker push $TAG
docker images