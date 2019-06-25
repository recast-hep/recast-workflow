import os
import glob


def make_input_yaml(point_path):
    input_yaml_path = os.path.join(point_path, 'input.yml')
    with open(os.path.join('templates', 'input.yml'), 'r') as f:
        text = f.read()
    text = text.replace('$HEPMC', os.path.join(point_path, 'output.hepmc'))
    with open(input_yaml_path, 'w+') as f:
        f.write(text)

def main():
    point_paths = [os.path.basename(p) for p in glob.glob('mMed*')]
    for point_path in point_paths:
        make_input_yaml(point_path)

if __name__ == '__main__':
    main()
