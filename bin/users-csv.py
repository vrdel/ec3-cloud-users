#!/usr/bin/python

import argparse
import sys
import os
import csv

from ec3_cloud_users.log import Logger


def main():
    parser = argparse.ArgumentParser(description="""Load users from csv""")
    parser.add_argument('-f', dest='csvfile', metavar='users.csv', help='path to csv file with users', type=str, required=False)
    args = parser.parse_args()
    logger = Logger(os.path.basename(sys.argv[0]))
    lobj = Logger(sys.argv[0])
    logger = lobj.get()

    users = list()

    with open(args.csvfile) as fp:
        reader = csv.reader(fp.readlines(), delimiter=',')
        for row in reader:
            users.append(row)

    users = users[1:]
    print(users[0])

if __name__ == '__main__':
    main()

