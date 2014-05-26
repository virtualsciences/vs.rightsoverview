from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

try:
    from zope.site.hooks import getSite
except ImportError:
    from zope.app.component.hooks import getSite

class Rights(BrowserView):
    template = ViewPageTemplateFile('rights.pt')
    title = 'Title'
    description = 'Description'

    def __call__(self):
        return self.template()


class UserRights(Rights):
    '''
    '''
    title = 'Users / Groups'
    description = ''
    # description = ('This is an overview of the users with rights overrides on '
    #                'the share tab of content.')
    which = 'users'

    def results(self):
        acl_users = getToolByName(self.context, 'acl_users')
        prm = acl_users.portal_role_manager
        roles = [r for r in prm.listRoleIds() if r != 'Owner']
        _users = dict([(u.getUserName(), u) for u in acl_users.getUsers()])
        _groups = dict([(u.getUserName(), u) for u in acl_users.getGroups()
            if [r for r in u.getRoles() if r != 'Authenticated']])
        principals = dict(
            (r, prm._safeListAssignedPrincipals(r)) for r in roles)
        all_users = set()
        for usergroup in principals.values():
            all_users |= set(usergroup)

        i, groups, gusers = 1, {}, {}
        for g in _groups.values():
            groups[g.getGroupId()] = i
            for uid in [u.id for u in g.getAllGroupMembers()]:
                _u = gusers.get(uid, {})
                for r in g.getRoles():
                    if r in roles:
                        _u[r] = _u.get(r, []) + [str(i)]
                if _u:
                    gusers[uid] = _u
            i += 1

        head = ['Who'] + roles
        _tu = '<a href="@@usergroup-userprefs?searchstring=%s">%s</a>'
        _tg = '<a href="@@usergroup-groupprefs?searchstring=%s">%s</a>'
        _gn = '<sup>%s</sup>'
        _gr = '<span class="discreet" style="text-align: left;">%s</span>'
        # Try to find the user in users, first by name, then by id. 
        # Then see if the user listed eroniously (e.g. not found), and finish 
        # with creating a url with the fingers crossed (LDAP users can be none 
        # of the above and then have the default LDAP userrights).
        user = lambda u: [
             u[0] in _users and _tu % (_users[u[0]], u[0]) or
             u[1] in _users and _tu % (_users[u[1]], u[0]) or
             u[1].endswith(': not found>') and ' '.join((u[0], '*')) or
             _tu % (u[1], u[0])]
        # Format with role and the group numbers giving the role for users
        # getting rights from groups.
        gr = lambda x, r: _gr % ' '.join([r, _gn % ', '.join(x)]) if x else ''
        ur = lambda x, r: ' '.join([r, _gn % ', '.join(x)]) if x else r
        role_list = lambda u: [(
            ur((gusers.get(u[0], {}) or gusers.get(u[1], {})).get(r, []), r
                ) if u in principals[r] else 
            gr((gusers.get(u[0], {}) or gusers.get(u[1], {})).get(r, []), r))
            for r in roles]

        body = [user(u) + role_list(u) for u in sorted(list(all_users)) 
                if u[0] not in _groups]

        return {'head': head, 'body': body, 'groups': groups}


class ShareRights(Rights):
    ''''''
    title = 'Sharing'
    description = ''
    # description = ('This is an overview of the users with rights overrides on '
    #                'the share tab of content.')
    which = 'shared'

    def get_name(self, id):
        member_info = self.pm.getMemberInfo(id)

        # member_info is None if there's no Plone user object, as when
        # using OpenID.
        if member_info:
            fullname = member_info.get('fullname', '')
            if fullname:
                return fullname

        return id

    def parse_results(self, results):
        roles = [u'Contributor', u'Editor', u'Reader', u'Reviewer']
        head = [u'Where', u'Who'] + roles
        body = []
        userdata = {}

        for r in results:
            path, url = r.getPath(), r.getURL()
            where = '<a href="%s">%s</a>' % ('/'.join((url, '@@sharing')),
                                             path)

            for s in r['Sharing']:
                if r['Sharing']:
                    type, id, title, share = s.split('|')
                    share = [['v', ' ', 'global', 'aquired']['tfga'.find(i)]
                             for i in share]
                    if 'v' in share:
                        type = 'Group' if type == 'g' else 'User'
                        contributor, editor, reader, reviewer = share
                        body.append([where, title, contributor, editor, reader,
                                     reviewer])

        return {'head': head, 'body': body}

    def results(self):
        self.catalog = getToolByName(self.context, 'portal_catalog')
        self.pm = getToolByName(self.context, 'portal_membership')

        return self.parse_results(self.catalog(sort_on='path'))
