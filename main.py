from utils.simulation import HarborSimulation
from statistics import mean
import argparse
from utils.cprint import cprint, BColors


def main(args):
    time_in_harbor = []
    time_in_dock = []

    for i in range(args.repetitions):
        if args.verbosity:
            cprint(BColors.BOLD, '*' * 50)
            cprint(BColors.BOLD, f'Harbor Simulation {i + 1}')
            cprint(BColors.BOLD, '*' * 50)

        harbor = HarborSimulation(args.ships, args.docks, args.verbosity)
        harbor.loop()
        time_in_harbor.extend([harbor.time_in_harbor(i) / 60 for i in range(args.ships)])
        time_in_dock.extend([harbor.time_in_dock(i) / 60 for i in range(args.ships)])

    mh = mean(time_in_harbor)
    md = mean(time_in_dock)
    cprint(BColors.OKGREEN, f'\n\nMean time in harbor {mh}')
    cprint(BColors.OKGREEN, f'Mean time in dock {md}')


def parse_args():
    parser = argparse.ArgumentParser(description='Overloaded Harbor Simulation')
    parser.add_argument('-s', '--ships', type=int, default=3, help='Number of ships')
    parser.add_argument('-d', '--docks', type=int, default=3, help='Number of docks in the harbor')
    parser.add_argument('-r', '--repetitions', type=int, default=10, help='Number of simulations')
    parser.add_argument('-v', '--verbosity', type=int, default=1, help='Verbosity level (0 disabled, 1 enabled)')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    main(args)

