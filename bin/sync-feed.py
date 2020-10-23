#!/usr/bin/python

from datetime import datetime
from unidecode import unidecode

from ec3_cloud_users.cache import load, update
from ec3_cloud_users.config import parse_config
from ec3_cloud_users.log import Logger

import argparse
import requests
import sys
import json
import errno


connection_timeout = 120
conf_opts = parse_config()


def fetch_feeddata(subscription, logger):
    try:
        response = requests.get(subscription, timeout=connection_timeout, verify=False)
        response.raise_for_status()

        return response.json()

    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        logger.error('requests error: %s' % e)
        raise SystemExit(1)

    except Exception as e:
        logger.error(e)


def gen_username(name, surname, existusers):
    # ASCII convert
    name = name.lower()
    surname = surname.lower()
    # take first char of name and first seven from surname
    username = name[0] + surname[:7]

    if username not in existusers:
        return username

    elif username in existusers:
        match = list()
        if len(username) < 8:
            match = filter(lambda u: u.startswith(username), existusers)
        else:
            match = filter(lambda u: u.startswith(username[:-1]), existusers)

        return username + str(len(match))


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
    lobj = Logger(sys.argv[0])
    logger = lobj.get()

    cachedb = conf_opts['settings']['cache']
    targetproject = conf_opts['external']['project']
    homeprefix = conf_opts['settings']['homeprefix']
    newusers = []

    parser = argparse.ArgumentParser(description="ec3-cloud-users sync json cache with feed data")
    parser.add_argument('-d', required=False, help='JSON cache file', dest='cache')
    parser.add_argument('-v', required=False, default=False,
                        action='store_true', help='Verbose', dest='verbose')
    args = parser.parse_args()

    data = fetch_feeddata(conf_opts['external']['subscription'], logger)

    if args.cache:
        cachedb = args.cache

    cache = load(cachedb, logger)

    for project in data:
        # skip projects that have not been accepted yet or are HTC only
        if project['sifra'] == targetproject:
            logger.info('Fetched project = %s' % project['sifra'])
            allusersdb = cache['users']
            usersdb = set([ue['uid'] - 1000 for ue in allusersdb])
            usersfeed = list()
            diff = set()
            usersfeed = set([int(uf['id']) for uf in project['users']])
            diff = usersfeed.difference(usersdb)

            allusernames = set([user['username'] for user in allusersdb])
            for user in diff:
                userfeed = filter(lambda u: user == u['id'], project['users'])[0]
                feedname = concat(unidecode(userfeed['ime']))
                feedsurname = concat(unidecode(userfeed['prezime']))
                feedemail = userfeed['mail']

                username = gen_username(feedname, feedsurname, allusernames)
                u = dict(
                    username=username,
                    name=feedname, surname=feedsurname, email=feedemail, shell=None,
                    homedir='{}/{}'.format(homeprefix, username), password=None,
                    uid=userfeed['id'] + 1000, gid=100, ispasswordset=False,
                    ishomecreated=False, issgeadded=False, issentemail=False,
                    date_created=datetime.now().strftime('%Y-%m-%d %H:%m:%s'),
                    status=int(userfeed['status_id']),
                    project=project['sifra'],
                )
                newusers.append(u)

    if newusers:
        logger.info("New users added into cache: %s" %
                    str_iterable([user['username'] for user in newusers]))
        cache['users'] = cache['users'] + newusers
        update(cachedb, cache, logger)
    else:
        logger.info("Cache up to date")


if __name__ == '__main__':
    main()
