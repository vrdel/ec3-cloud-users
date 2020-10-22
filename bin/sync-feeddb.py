#!/usr/bin/python

import __main__
__main__.__requires__ = __requires__ = []
__requires__.append('SQLAlchemy >= 0.8.2')
import pkg_resources
pkg_resources.require(__requires__)

from sqlalchemy import create_engine, and_
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from datetime import datetime
from unidecode import unidecode

from ec3_cloud_users.cachedb import Base, User
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


def update_cache_json(cache, newusers, logger):
    try:
        with open(cache, mode='w') as fp:
            json.dump(newusers, fp, indent=4)

    except IOError as exc:
        logger.error('Error opening cache')
        logger.error(exc)
        raise SystemExit(1)


def load_cache_json(cache, logger):
    try:
        with open(cache, mode='r') as fp:
            return json.loads(fp.read())

    except IOError as exc:
        if exc.errno == errno.ENOENT:

            logger.info('Creating %s for first time' % cache)
            emptyusers = {'users': []}

            with open(cache, mode='w+') as fp:
                json.dump(emptyusers, fp, indent=4)

            return emptyusers
        else:
            logger.error(exc)
            raise SystemExit(1)


def main():
    lobj = Logger(sys.argv[0])
    logger = lobj.get()

    cachedb = conf_opts['settings']['cache']
    targetproject = conf_opts['external']['project']
    newusers = []

    parser = argparse.ArgumentParser(description="ec3-cloud-users sync DB")
    parser.add_argument('-d', required=False, help='SQLite DB file', dest='sql')
    parser.add_argument('-v', required=False, default=False,
                        action='store_true', help='Verbose', dest='verbose')
    args = parser.parse_args()

    data = fetch_feeddata(conf_opts['external']['subscription'], logger)

    if args.sql:
        cachedb = args.sql

    # engine = create_engine('sqlite:///%s' % cachedb, echo=args.verbose)
    cache = load_cache_json(cachedb, logger)

    for project in data:
        # skip projects that have not been accepted yet or are HTC only
        if project['sifra'] == targetproject:
            logger.info('Fetched project = %s' % project['sifra'])
            allusersdb = cache['users']
            usersdb = set([ue.uid - 1000 for ue in allusersdb])
            usersfeed = list()
            diff = set()
            usersfeed = set([int(uf['id']) for uf in project['users']])
            diff = usersfeed.difference(usersdb)

            allusernames = set([user.username for user in allusersdb])
            for user in diff:
                userfeed = filter(lambda u: user == u['id'], project['users'])[0]
                feedname = concat(unidecode(userfeed['ime']))
                feedsurname = concat(unidecode(userfeed['prezime']))
                feedemail = userfeed['mail']

                username = gen_username(feedname, feedsurname, allusernames)
                u = dict(
                    username=username,
                    name=feedname, surname=feedsurname, email=feedemail, shell=None,
                    homedir='/home/{}'.format(username), password=None,
                    uid=userfeed['id'] + 1000, gid=100,
                    issubscribe=0, ispasswordset=0, ishomecreated=0,
                    issgeadded=0, issentemail=0,
                    date_created=datetime.now().strftime('%Y-%m-%d %H:%m:%s'),
                    status=int(userfeed['status_id']),
                    project=project['sifra'],
                )
                newusers.append(u)

    if newusers:
        logger.info("New users added into cache: %s" %
                    str_iterable([user['username'] for user in newusers]))
        cache['users'].append(newusers)
        update_cache_json(cachedb, cache, logger)
    else:
        logger.info("Cache up to date")


if __name__ == '__main__':
    main()
