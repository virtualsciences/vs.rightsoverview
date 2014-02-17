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
        _groups = dict([(u.getUserName(), u) for u in acl_users.getGroups()])
        principals = dict((r, prm.listAssignedPrincipals(r)) for r in roles)
        all_users = set()
        for usergroup in principals.values():
            all_users |= set(usergroup)

        head = ['Who'] + roles
        _tu = '<a href="@@usergroup-userprefs?searchstring=%s">%s</a>'
        _tg = '<a href="@@usergroup-groupprefs?searchstring=%s">%s</a>'
        body = [[u[0] in _groups and _tg % (_groups[u[0]], u[0]) or
                 u[0] in _users and _tu % (_users[u[0]], u[0]) or
                 u[1] in _users and _tu % (_users[u[1]], u[0]) or
                 u[1].endswith(': not found>') and u[0] + ' *' or u] +
                [(r if u in principals[r] else '') for r in roles]
                for u in sorted(list(all_users))]

        return {'head': head, 'body': body}

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
