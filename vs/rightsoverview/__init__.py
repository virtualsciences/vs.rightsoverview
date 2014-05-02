from Acquisition import aq_parent, aq_inner
from plone.app.workflow.browser.sharing import SharingView
from Products.PluggableAuthService.plugins.ZODBRoleManager import (
    ZODBRoleManager, ManageUsers)

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

def __call_m_for_monkey__(self):
    """Perform the update and redirect if necessary, or render the page
    """
    postback = self.handle_form()
    if 'form.button.Save' in self.request.form:
        self.context.aq_inner.reindexObject()
    if postback:
        return self.index()
    else:
        context_state = self.context.restrictedTraverse(
            "@@plone_context_state")
        url = context_state.view_url()
        self.request.response.redirect(url)

SharingView.__call__ = __call_m_for_monkey__

def _safeListAssignedPrincipals( self, role_id ):
    result = []

    for k, v in self._principal_roles.items():
        if role_id in v:
            # should be at most one and only one mapping to 'k'

            parent = aq_parent( self )
            info = parent.searchPrincipals( id=k, exact_match=True )

            if len( info ) == 0:
                title = '<%s: not found>' % k
            else:
                title = info[0].get( 'title', k )
            result.append( ( k, title ) )

    return result

ZODBRoleManager._safeListAssignedPrincipals = _safeListAssignedPrincipals
