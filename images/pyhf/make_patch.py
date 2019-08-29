import pyhf
import json

import argparse


def make_patch(workspace, signal_json, output):
    pass    

def main():
    parser = argparse.ArgumentParser(
        description='Create a json patch from generic json output for a pyhf workspace. \
            Will attempt to match json histograms with samples from the pyhf workspace.')
    parser.add_argument(
        'workspace', help='A path to a valid json workspace for pyhf.')
    parser.add_argument(
        'signal_json', help='A path to a json file containing \
            the signal histograms that should be patched into the workspace.')
    parser.add_argument('output', help='The output patch file.')
    args = parser.parse_args()
    make_patch(args.workspace, args.yoda, args.output)
    