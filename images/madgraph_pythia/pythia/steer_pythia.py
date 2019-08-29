#!/usr/bin/env python
import argparse
import subprocess
import shlex


def runpythia(inputlhe, outputhepmc, nevents):
    raise NotImplementedError('Make pythia card be an input.')
    runcardtmpl = 'pythia.tmpl'
    runcardname = 'pythia_card.dat'
    with open(runcardtmpl, 'r') as template:
        with open(runcardname, 'w+') as filled:
            filled.write(template.read().format(
                LHEF=inputlhe, NEVENTS=nevents))
    subprocess.check_call(shlex.split(
        './pythia8/examples/main42 {} {}'.format(runcardname, outputhepmc)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Steer pythia8.')
    parser.add_argument('inputlhe', help='Path to input LHE file.')
    parser.add_argument('outputhepmc', help='Path to output hepmc file.')
    parser.add_argument('nevents', help='number of events.')
    args = parser.parse_args()
    runpythia(args.inputlhe, args.outputhepmc, args.nevents)
