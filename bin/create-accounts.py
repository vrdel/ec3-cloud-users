#!/usr/bin/python

import __main__
__main__.__requires__ = __requires__ = []
__requires__.append('SQLAlchemy >= 0.8.2')
import pkg_resources
pkg_resources.require(__requires__)

import argparse

from ec3_cloud_users.cachedb import User
from ec3_cloud_users.userutils import UserUtils
from ec3_cloud_users.log import Logger
from ec3_cloud_users.config import parse_config
from ec3_cloud_users.msg import InfoAccOpen

from unidecode import unidecode

from base64 import b64encode

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
import requests
import shutil
import subprocess

connection_timeout = 120
conf_opts = parse_config()


def gen_password():
    s = os.urandom(64)

    return b64encode(s)[:30]


def create_homedir(dir, uid, gid, logger):
    try:
        os.mkdir(dir, 0750)
        os.chown(dir, uid, gid)

        for root, dirs, files in os.walk(conf_opts['settings']['skeletonpath']):
            for f in files:
                shutil.copy(root + '/' + f, dir)
                os.chown(dir + '/' + f, uid, gid)

        return True

    except Exception as e:
        logger.error(e)

        return False


def main():
    lobj = Logger(sys.argv[0])
    logger = lobj.get()

    cdb = conf_opts['settings']['cache']

    parser = argparse.ArgumentParser(description="ec3-cloud-users update users DB")
    parser.add_argument('-d', required=False, help='SQLite DB file', dest='sql')
    parser.add_argument('-v', required=False, default=False,
                        action='store_true', help='Verbose', dest='verbose')
    args = parser.parse_args()

    if args.sql:
        cdb = args.sql

    engine = create_engine('sqlite:///%s' % cdb, echo=args.verbose)

    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    usertool = UserUtils(logger)

    if conf_opts['settings']['createhome']:
        # create /home directories for user
        not_home = session.query(User).filter(User.ishomecreated is False).all()
        for u in not_home:
            if (os.path.exists(u.homedir)):
                rh = True
            else:
                rh = create_homedir(u.homedir, u.uid, u.gid, logger)
            if rh is True:
                u.ishomecreated = True
                logger.info('Created directories for %s' % u.username)
        session.commit()

    if conf_opts['settings']['associatesgeproject']:
        # add users to SGE projects
        not_sge = session.query(User).filter(User.issgeadded is False).all()
        for u in not_sge:
            sgecreateuser_cmd = conf_opts['settings']['sgecreateuser']
            try:
                os.chdir(os.path.dirname(sgecreateuser_cmd))
                subprocess.check_call('{0} {1} {2}'.format(sgecreateuser_cmd,
                                                           u.username,
                                                           u.last_project),
                                      shell=True, bufsize=512)
                u.issgeadded = True
                logger.info('User %s added in SGE project %s' % (u.username, u.last_project))

            except Exception as e:
                logger.error('Failed adding user %s to SGE: %s' % (u.username, str(e)))
        session.commit()

    # set password for opened user accounts
    not_password = session.query(User).filter(User.ispasswordset is False).all()
    for u in not_password:
        password = gen_password()
        u.password = password
        usertool.set_user_pass(usertool.get_user(u.username), password)
        u.ispasswordset = True
    session.commit()

    if conf_opts['external']['sendemail']:
        # send email to user whose account is opened
        not_email = session.query(User).filter(User.issentemail is False).all()
        for u in not_email:
            templatepath = conf_opts['external']['emailtemplate']
            smtpserver = conf_opts['external']['emailsmtp']
            emailfrom = conf_opts['external']['emailfrom']
            emailsubject = conf_opts['external']['emailsubject']

            e = InfoAccOpen(u.username, u.password, templatepath, smtpserver,
                            emailfrom, u.email, emailsubject, logger)
            r = e.send()
            if r:
                u.issentemail = True
                logger.info('Mail sent for %s' % u.username)
        session.commit()


if __name__ == '__main__':
    main()
