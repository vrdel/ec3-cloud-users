#!/usr/bin/python

import argparse

from ec3_cloud_users.cache import load, update
from ec3_cloud_users.userutils import UserUtils
from ec3_cloud_users.log import Logger
from ec3_cloud_users.config import parse_config
from ec3_cloud_users.msg import InfoAccOpen

from base64 import b64encode

import sys
import os
import requests
import shutil
import subprocess


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

    usertool = UserUtils(logger)
    cache = load(cdb, logger)

    allusers_passwd = set(usertool.all_users_list())
    allusers_db = set([u['username'] for u in cache['users']])
    diff = allusers_db.difference(allusers_passwd)

    # create user account (entries in /etc/passwd)
    for user in diff:
        userdb = filter(lambda u: u['username'] == user, cache['users'])[0]
        iscreated = usertool.add_user(user, userdb['uid'], userdb['gid'],
                                      userdb['name'], userdb['surname'],
                                      userdb['homedir'], userdb['project'])
        if iscreated:
            logger.info('Created user account for %s' % user)
        elif iscreated is False:
            logger.error('Problem creating user account for %s' % user)
        else:
            pass

    if conf_opts['settings']['setpassword']:
        # set password for opened user accounts
        not_password = filter(lambda u: u['ispasswordset'] == False, cache['users'])
        for u in not_password:
            password = gen_password()
            u['password'] = password
            usertool.set_user_pass(usertool.get_user(u['username']), password)
            u['ispasswordset'] = True
            logger.info('Set password for %s' % u['username'])
        if not_password:
            update(cdb, cache, logger)

    if conf_opts['settings']['createhome']:
        # create /home directories for user
        not_home = filter(lambda u: u['ishomecreated'] == False, cache['users'])
        for u in not_home:
            if (os.path.exists(u['homedir'])):
                rh = True
            else:
                rh = create_homedir(u['homedir'], u['uid'], u['gid'], logger)
            if rh is True:
                u['ishomecreated'] = True
                logger.info('Created home directory for %s' % u['username'])
            else:
                logger.error('Failed creating home directory for %s' % u['username'])
        if not_home:
            update(cdb, cache, logger)

    if conf_opts['settings']['associatesgeproject']:
        # add users to SGE projects
        not_sge = filter(lambda u: u['issgeadded'] == False, cache['users'])
        for u in not_sge:
            sgecreateuser_cmd = conf_opts['settings']['sgecreateuser']
            try:
                os.chdir(os.path.dirname(sgecreateuser_cmd))
                subprocess.check_call('{0} {1} {2}'.format(sgecreateuser_cmd,
                                                           u['username'],
                                                           u['project']),
                                      shell=True, bufsize=512)
                u['issgeadded'] = True
                logger.info('User %s added in SGE project %s' % (u['username'], u['project']))

            except Exception as e:
                logger.error('Failed adding user %s to SGE: %s' % (u['username'], str(e)))
        if not_sge:
            update(cdb, cache, logger)

    if conf_opts['external']['sendemail']:
        # send email to user whose account is opened
        not_email = filter(lambda u: u['issentemail'] == False, cache['users'])
        for u in not_email:
            templatepath = conf_opts['external']['emailtemplate']
            smtpserver = conf_opts['external']['emailsmtp']
            emailfrom = conf_opts['external']['emailfrom']
            emailsubject = conf_opts['external']['emailsubject']
            ipaddress = conf_opts['external']['ipaddress']

            e = InfoAccOpen(u['username'], u['password'], templatepath, smtpserver,
                            emailfrom, u['email'], emailsubject, ipaddress, logger)
            r = e.send()
            if r:
                u['issentemail'] = True
                logger.info('Mail sent for %s' % u['username'])
            else:
                logger.error('Failed mail sent for %s' % u['username'])
        if not_email:
            update(cdb, cache, logger)


if __name__ == '__main__':
    main()
