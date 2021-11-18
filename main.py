from utils.simulation import HarborSimulation
from logging import Logger
from statistics import mean
import argparse, os


def main(args):
    elapsed = []
    for _ in range(args.tries):
        print("Starting a new harbor simulation", 'Main  ')
        harbor = HarborSimulation(args.amount, args.docks)
        harbor.loop()
        elapsed.extend([harbor.elapsed(i) / 60 for i in range(args.amount)])

    ev = mean(elapsed)
    print(f"The mean of the ships turn around time is {ev} hours", 'Main  ')
    return ev


def parse_args():
    parser = argparse.ArgumentParser(description='Harbor simulator')
    parser.add_argument('-d', '--docks', type=int, default=3, help='number of harbor docks')
    parser.add_argument('-a', '--amount', type=int, default=3, help='number of ships to attend')
    parser.add_argument('-t', '--tries', type=int, default=10, help='number of harbor simulations')
    parser.add_argument('-l', '--level', type=str, default='INFO', help='log level')
    parser.add_argument('-F', '--file', type=bool, const=True, nargs='?', help='write the log in a file')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    if args.file:
        os.makedirs("./logs/", exist_ok=True)
    log = Logger(name='Harbor-Logguer')
    log.setLevel(args.level)

    ev = main(args)
    if args.file: 
        print(ev)
