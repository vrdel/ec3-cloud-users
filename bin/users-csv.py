#!/usr/bin/python

import argparse
import sys
import os
import csv

from ec3_cloud_users.log import Logger
from ec3_cloud_users.cache import load, update
from ec3_cloud_users.userutils import UserUtils
from ec3_cloud_users.config import parse_config
from ec3_cloud_users.userutils import gen_username

conf_opts = parse_config()


def main():
    parser = argparse.ArgumentParser(description="""Load users from csv""")
    parser.add_argument('-f', dest='csvfile', metavar='users.csv', help='path to csv file with users', type=str, required=False)
    args = parser.parse_args()
    logger = Logger(os.path.basename(sys.argv[0]))
    lobj = Logger(sys.argv[0])
    logger = lobj.get()

    usertool = UserUtils(logger)
    users, usernames = dict(), set()
    cdb = conf_opts['settings']['cache']
    cache = load(cdb, logger)
    targetproject = conf_opts['external']['project']
    homeprefix = conf_opts['settings']['homeprefix']

    allusernames_db = set([u['username'] for u in cache['users']])

    with open(args.csvfile) as fp:
        reader = csv.reader(fp.readlines(), delimiter=',')
        next(reader, None)
        for row in reader:
            users.update({
                gen_username(row[0], row[1], allusernames_db): {
                    'name': row[0],
                    'surname': row[1],
                    'email': row[2]
                }})

    import ipdb; ipdb.set_trace()

    for user in users:
        usernames.update([user['username']])

    diff = usernames.difference(allusernames_db)
    print(diff)

    # for user in diff:
        # u = dict(
            # username=username,
            # name=feedname, surname=feedsurname, email=feedemail, shell=None,
            # homedir='{}/{}'.format(homeprefix, username), password=None,
            # uid=userfeed['id'] + 2000, gid=100, ispasswordset=False,
            # ishomecreated=False, issgeadded=False, issentemail=False,
            # date_created=datetime.now().strftime('%Y-%m-%d %H:%m:%s'),
            # status=int(userfeed['status_id']),
            # project=project['sifra'],
        # )
        # newusers.append(u)


if __name__ == '__main__':
    main()
