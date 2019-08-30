import argparse
import yoda
import json
import re


def convert_yoda_to_json(yoda_path, json_path):
    with open(json_path, 'w+') as f:
        json_serializable = {}
        for k,v in yoda.read(yoda_path).items():
            if type(v) == yoda.core.Histo1D:
                json_serializable[k] = [b.sumW for b in v.bins]
            elif type(v) == yoda.core.Scatter1D:
                json_serializable[k] = [p.x for p in v.points]
            elif type(v) == yoda.core.Scatter2D:
                json_serializable[k] = [(p.x, p.y) for p in v.points]
            elif type(v) == yoda.core.Profile1D:
                json_serializable[k] = [b.sumWY for b in v.bins]
            elif type(v) == yoda.core.Counter:
                json_serializable[k] = v.val
            else:
                print('WARNING: yoda object of type {} encountered (no known conversion)! Object is being ignored...'.format(type(v)))
        json.dump(json_serializable, f, sort_keys=True)


def main():
    parser = argparse.ArgumentParser(
        description='Convert yoda file into generic json file mapping histogram names to data.')
    parser.add_argument('yoda', help='path to input yoda file.')
    parser.add_argument('json', help='path to output json file.')
    args = parser.parse_args()
    convert_yoda_to_json(args.yoda, args.json)


if __name__ == '__main__':
    main()
