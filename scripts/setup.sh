DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export PYTHONPATH=$PYTHONPATH:$(realpath $DIR/..)
export WORKON_HOME=$HOME/.local/share/.virtualenvs