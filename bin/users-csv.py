#!/usr/bin/python

import argparse
import sys
import os
import csv

from unidecode import unidecode
from ec3_cloud_users.log import Logger
from ec3_cloud_users.cache import load, update
from ec3_cloud_users.userutils import UserUtils
from ec3_cloud_users.config import parse_config
from ec3_cloud_users.userutils import gen_username
from datetime import datetime

conf_opts = parse_config()


def calc_next_uid(list_users):
    if len(list_users) > 0:
        last = [user for user in list_users if user['uid'] > 2000]
        return last[-1]['uid'] + 1 if len(last) > 0 else 2000
    else:
        return 2000


def concat(s):
    if '-' in s:
        s = s.split('-')
        s = ''.join(s)
    if ' ' in s:
        s = s.split(' ')
        s = ''.join(s)

    return s

def str_iterable(s):
    return ', '.join(s)


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
    next_uid = None

    allusernames_db = set([u['username'] for u in cache['users']])
    allnames_db = set(['{}{}'.format(u['name'], u['surname']) for u in cache['users']])

    with open(args.csvfile) as fp:
        reader = csv.reader(fp.readlines(), delimiter=',')
        next(reader, None)
        for row in reader:
            name = concat(unidecode(unicode(row[0], 'utf-8')))
            surname = concat(unidecode(unicode(row[1], 'utf-8')))
            userkey = '{}{}'.format(name, surname)
            if userkey in allnames_db:
                continue

            username = gen_username(name, surname, allusernames_db)
            users.update({
                userkey: {
                    'name': name,
                    'surname': surname,
                    'email': row[2],
                    'username': username
                }})
            users.update({
                username: {
                    'name': name,
                    'surname': surname,
                    'email': row[2],
                    'username': username
                }})

    for user in users:
        usernames.update([users[user]['username']])

    diff = usernames.difference(allusernames_db)

    next_uid = calc_next_uid(cache['users'])

    newusers = list()
    for user in diff:
        u = dict(
            username=users[user]['username'], name=users[user]['name'],
            surname=users[user]['surname'],
            email=users[user]['email'], shell=None,
            homedir='{}/{}'.format(homeprefix, username), password=None,
            uid=next_uid, gid=100, ispasswordset=False, ishomecreated=False,
            issgeadded=False, issentemail=False,
            date_created=datetime.now().strftime('%Y-%m-%d %H:%m:%s'),
            status=1, project=targetproject,
        )
        newusers.append(u)
        next_uid += 1

    if newusers:
        logger.info("New users added into cache: %s" %
                    str_iterable([user['username'] for user in newusers]))
        cache['users'] = cache['users'] + newusers
        update(cdb, cache, logger)
    else:
        logger.info("Cache up to date")


if __name__ == '__main__':
    main()
