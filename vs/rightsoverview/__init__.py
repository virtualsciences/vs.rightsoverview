from plone.app.workflow.browser.sharing import SharingView

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
