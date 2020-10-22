import json
import errno


def update(cache, newusers, logger):
    try:
        with open(cache, mode='w') as fp:
            json.dump(newusers, fp, indent=4)

    except IOError as exc:
        logger.error('Error opening cache')
        logger.error(exc)
        raise SystemExit(1)


def load(cache, logger):
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
            logger.error('Error loading cache')
            logger.error(exc)
            raise SystemExit(1)

