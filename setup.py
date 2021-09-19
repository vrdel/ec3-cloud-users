from distutils.core import setup
import glob

NAME = 'ec3-cloud-users'


def get_ver():
    try:
        for line in open(NAME + '.spec'):
            if "Version:" in line:
                return line.split()[1]
    except IOError:
        print "Make sure that %s is in directory" % (NAME + '.spec')
        raise SystemExit(1)


setup(name=NAME,
      version=get_ver(),
      author='SRCE',
      author_email='dvrcic@srce.hr',
      description='Scripts for opening user accounts on EC3 cluster of SRCE HTC Cloud',
      url='https://github.com/vrdel/ec3-cloud-users',
      package_dir={'ec3_cloud_users': 'modules/'},
      packages=['ec3_cloud_users'],
      data_files=[('/etc/%s' % NAME, glob.glob('config/*')),
                  ('/usr/libexec/%s' % NAME, ['bin/create-accounts.py',
                                              'bin/sync-feed.py',
                                              'bin/users-csv.py']),
                  ('/etc/cron.d/', ['cron/ec3-cloud-users']),
                  ('/usr/libexec/%s/sgetools/' % NAME, glob.glob('helpers/sgetools/*')),
                  ])
