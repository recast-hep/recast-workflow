POINT_DIR=$1
WORKDIR=workdir_${POINT_DIR}
rm -rf $WORKDIR
yadage-run $WORKDIR workflow.yml $POINT_DIR/input.yml -t ../../../analysis/rivet -d initdir=$PWD
mv $WORKDIR/madgraph_pythia/output.hepmc $POINT_DIR
