import argparse
import os
import shutil
import subprocess
import glob


def edit_proc_card(proc_card_path, param_card_path, run_card_path, shower_card_path, shower, n_events):
    with open(proc_card_path, 'a') as f:
        f.write('output output\n')
        f.write('launch\n')
        if shower:
            f.write('shower=Pythia8\ndone\n')
        else:
            f.write('shower=OFF\ndone\n')
        # Read from the given cards and set the number of events.
        if param_card_path is not None and param_card_path != "default":
            f.write('{}\n'.format(param_card_path))
        if run_card_path is not None and run_card_path != "default":
            f.write('{}\n'.format(run_card_path))
        if shower and shower_card_path is not None and shower_card_path != "default":
            f.write('{}\n'.format(shower_card_path))
        if n_events is not None:
            f.write('set nevents {}\n'.format(n_events))
        f.write('0\n')


def run_madgraph(proc_card_path, output_path, ufotar, param_card_path=None, run_card_path=None, shower_card_path=None, shower=False, n_events=None):
    print('cwd={}'.format(os.getcwd()))
    print('ufotar={}'.format(ufotar))
    print('proc_card={}'.format(proc_card_path))
    print('param_card={}'.format(param_card_path))
    print('run_card={}'.format(run_card_path))
    if ufotar is not None and ufotar != "default":
        if '/' in ufotar:
            ufo_name, ufo_ext = os.path.splitext(os.path.basename(ufotar))
        else:
            ufo_name, ufo_ext = os.path.splitext(ufotar)
        assert ufo_ext == '.tar', 'ufo must be a tar file!'
        subprocess.call(['tar', '-xvf', ufotar])
        ufo_path = 'madgraph/models/{}'.format(ufo_name)
        shutil.rmtree(ufo_path, ignore_errors=True)
        shutil.copytree(ufo_name, ufo_path)
    proc_card_copy_path = os.path.join(os.getcwd(), 'proc_card.dat')
    shutil.copyfile(proc_card_path, proc_card_copy_path)
    edit_proc_card(proc_card_copy_path, param_card_path,
                   run_card_path, shower_card_path, shower, n_events)
    subprocess.call(['/code/madgraph/bin/mg5_aMC', proc_card_copy_path])
    run_dir = os.path.join(os.getcwd(), 'output', 'Events', 'run_01')
    event_path = glob.glob(os.path.join(run_dir, '*.lhe.gz'))[0]
    subprocess.call(['gunzip', event_path])
    event_path = glob.glob(os.path.join(run_dir, '*.lhe'))[0]
    subprocess.call('cp {} {}'.format(event_path, output_path), shell=True)


def main():
    parser = argparse.ArgumentParser(description='Run madgraph+pythia.')
    parser.add_argument('proc_card', help='path to proc_card.')
    parser.add_argument('output', help='path for output LHE.')
    parser.add_argument('--ufotar', help='path to UFO tar file.')
    parser.add_argument(
        '--param_card', help='path to param_card. Leave unspecified or pass "default" to use the default param card for the model.')
    parser.add_argument(
        '--run_card', help='path to run_card. Leave unspecified or pass "default" to use the default run card for the model.')
    parser.add_argument('--n_events', '-n', type=int, help='Number of events.')
    parser.add_argument('--shower', help='If true, use pythia to shower the particles.', action='store_true')
    parser.add_argument(
        '--shower_card', help='path to shower_card. Leave unspecified or pass "default" to use the default shower card for the model.')
    args = parser.parse_args()
    run_madgraph(args.proc_card, args.output, args.ufotar,
                 args.param_card, args.run_card, args.shower_card, args.shower, args.n_events)


if __name__ == '__main__':
    main()
