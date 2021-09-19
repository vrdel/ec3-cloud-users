import libuser


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


class UserUtils(object):
    def __init__(self, logger, home_prefix='/home'):
        self.logger = logger
        self.home_prefix = home_prefix

    def get_user(self, username):
        user = libuser.admin().lookupUserByName(username)
        return user

    def all_users_list(self):
        users = libuser.admin().enumerateUsersFull()
        users = [u for u in users if self.get_user_home(u).startswith('/home')]
        users = [self.get_user_name(u) for u in users]
        return users

    def all_users(self):
        users = libuser.admin().enumerateUsersFull()
        users = [u for u in users if self.get_user_home(u).startswith('/home')]
        return users

    def all_projects_users(self):
        projects = dict()
        users = self.all_users()

        for u in users:
            name, surname, project = self.info_comment(u)

            if project in projects:
                projects[project].append(self.get_user_name(u))
            else:
                projects[project] = list()
                projects[project].append(self.get_user_name(u))

        return projects

    def info_comment(self, userobj):
        comment = self.get_user_comment(userobj)
        name, surname, project = '', '', ''
        if comment:
            try:
                if ',' in comment:
                    fullname, project = map(lambda x: x.strip(), comment.split(','))
                    name, surname = fullname.split(' ')
                else:
                    name, surname = comment.split(' ')
            except ValueError as e:
                self.logger.error('{0}.{1}: user={2} {3}'.format(self.__class__.__name__,
                                                                 'info_comment',
                                                                 self.get_user_name(userobj),
                                                                 str(e)))

        return name, surname, project

    def get_user_home(self, userobj):
        try:
            return userobj.get(libuser.HOMEDIRECTORY)[0]

        except IndexError as e:
            self.logger.error('{0}.{1}: user={2} {3}'.format(self.__class__.__name__,
                                                             'get_user_home',
                                                             self.get_user_name(userobj),
                                                             str(e)))

    def set_user_comment(self, userobj, name, surname, project):
        userobj[libuser.GECOS] = '{} {}, {}'.format(name, surname, project)

    def add_user(self, username, uid, gid, name, surname, homedir, project):
        newuser = libuser.admin().initUser(username)
        newuser[libuser.UIDNUMBER] = long(uid)
        newuser[libuser.GIDNUMBER] = long(gid)
        newuser[libuser.HOMEDIRECTORY] = [homedir]
        self.set_user_comment(newuser, name, surname, project)

        try:
            ret = libuser.admin().addUser(newuser, False, True)
        except RuntimeError as excp:
            if 'entry already present' in excp.message:
                # silent about it
                return None
            else:
                self.logger.warning(excp)
                return False

        return ret

    def get_user_name(self, userobj):
        return userobj.get(libuser.USERNAME)[0]

    def get_user_id(self, userobj):
        return userobj.get(libuser.UIDNUMBER)[0]

    def get_group_id(self, userobj):
        return userobj.get(libuser.GIDNUMBER)[0]

    def get_user_pass(self, userobj):
        return userobj.get(libuser.SHADOWPASSWORD)[0]

    def get_user_comment(self, userobj):
        return userobj.get(libuser.GECOS)[0]

    def set_user_pass(self, userobj, password):
        libuser.admin().setpassUser(userobj, password, False)

    def get_user_shell(self, userobj):
        return userobj.get(libuser.LOGINSHELL)[0]
