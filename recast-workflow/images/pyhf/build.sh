PYHF_VERSION=$1
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TAG="recast/pyhf:v$PYHF_VERSION"

echo "$DOCKER_PASSWORD" | docker login --username $DOCKER_USERNAME --password-stdin
echo "PYHF_VERSION is ${PYHF_VERSION}"
docker build -t $TAG --build-arg PYHF_VERSION=$PYHF_VERSION $DIR
docker push $TAG
docker images