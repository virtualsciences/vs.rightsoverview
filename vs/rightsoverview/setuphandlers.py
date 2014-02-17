from Products.CMFCore.utils import getToolByName

def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('vs.rightsoverview_various.txt') is None:
        return

    catalog = getToolByName(context, 'portal_catalog')
    catalog.manage_catalogReindex()


