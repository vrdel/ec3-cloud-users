import ConfigParser
import sys
import os

conf = '/etc/ec3-cloud-users/config.conf'


def parse_config(logger=None):
    confopts = dict()

    try:
        config = ConfigParser.ConfigParser()
        if config.read(conf):
            for section in config.sections():
                if section.startswith('external'):
                    confopts['external'] = ({'subscription': config.get(section, 'subscription')})
                    confopts['external'].update({'sendemail': config.getboolean(section, 'sendemail')})
                    confopts['external'].update({'ipaddress': config.get(section, 'ipaddress')})
                    confopts['external'].update({'project': config.get(section, 'project')})
                    confopts['external'].update({'emailfrom': config.get(section, 'emailfrom')})
                    confopts['external'].update({'emailsubject': config.get(section, 'emailsubject')})
                    confopts['external'].update({'emailsmtp': config.get(section, 'emailsmtp')})
                    confopts['external'].update({'emailtemplate': config.get(section, 'emailtemplate')})
                    if not os.path.exists(confopts['external']['emailtemplate']):
                        if logger:
                            logger.error('%s does not exist' % confopts['external']['emailtemplate'])
                        else:
                            sys.stderr.write('%s does not exist\n' % confopts['external']['emailtemplate'])
                        raise SystemExit(1)

                if section.startswith('settings'):
                    confopts['settings'] = {'gid': config.getint(section, 'gid')}
                    confopts['settings'].update({'createhome': config.getboolean(section, 'createhome')})
                    confopts['settings'].update({'associatesgeproject': config.getboolean(section, 'associatesgeproject')})
                    confopts['settings'].update({'homeprefix': config.get(section, 'homeprefix')})

                    skeletonpath = config.get(section, 'skeletonpath')
                    if not skeletonpath.endswith('/'):
                        skeletonpath = skeletonpath + '/'
                    confopts['settings'].update({'skeletonpath': skeletonpath})
                    if not os.path.exists(confopts['settings']['skeletonpath']):
                        if logger:
                            logger.error('%s does not exist' % confopts['settings']['skeletonpath'])
                        else:
                            sys.stderr.write('%s does not exist\n' % confopts['settings']['skeletonpath'])
                        raise SystemExit(1)

                    sgecreateuser = config.get(section, 'sgecreateuser')
                    confopts['settings'].update({'sgecreateuser': sgecreateuser})
                    if not os.path.exists(confopts['settings']['skeletonpath']):
                        if logger:
                            logger.error('%s does not exist' % confopts['settings']['sgecreateuser'])
                        else:
                            sys.stderr.write('%s does not exist\n' % confopts['settings']['sgecreateuser'])
                        raise SystemExit(1)

                    cache = config.get(section, 'cache')
                    confopts['settings'].update({'cache': cache})
            return confopts

        else:
            if logger:
                logger.error('Missing %s' % conf)
            else:
                sys.stderr.write('Missing %s\n' % conf)
            raise SystemExit(1)

    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as e:
        if logger:
            logger.error(e)
        else:
            sys.stderr.write('%s\n' % e)
        raise SystemExit(1)

    except (ConfigParser.MissingSectionHeaderError, ConfigParser.ParsingError, SystemExit) as e:
        if getattr(e, 'filename', False):
            if logger:
                logger.error(e.filename + ' is not a valid configuration file')
                logger.error(' '.join(e.args))
            else:
                sys.stderr.write(e.filename + ' is not a valid configuration file\n')
                sys.stderr.write(' '.join(e.args) + '\n')
        raise SystemExit(1)

    return confopts
