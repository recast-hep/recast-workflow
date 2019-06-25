POINT_DIR=$1
WORKDIR="workdir_$(basename -- $POINT_DIR)"
rm -rf $WORKDIR
yadage-run $WORKDIR workflow.yml $POINT_DIR/input.yml -t ../../../generation/madgraph_pythia -d initdir=$PWD
mv $WORKDIR/madgraph_pythia/output.hepmc $POINT_DIR
