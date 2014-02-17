from plone.indexer.decorator import indexer
from zope.interface import Interface

def parse_shares(shares):
    res = []

    for share in shares:
        type = share['type'][0].lower()
        role_map = share['roles']
        roles = ''.join([str(role_map[k])[0].lower()
                         for k in sorted(role_map.keys())])
        res.append('|'.join([type, share['id'], share['title'], roles]))

    return res

@indexer(Interface)
def sharing(obj):
    return parse_shares(
        obj.restrictedTraverse('@@sharing').existing_role_settings())