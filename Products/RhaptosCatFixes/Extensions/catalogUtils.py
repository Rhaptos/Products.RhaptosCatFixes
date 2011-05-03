from StringIO import StringIO

def checkCatalog(self):
    out = StringIO()
    catalog = self.portal_catalog._catalog
    idx = catalog.schema['portal_type']
    stale = 0
    pfactory = 0
    pcp = 0
    cdoc = 0
    for uid, rid in catalog.uids.items():
        val = catalog.data[rid][idx]
        if val == 'PublishedContentPointer':
            pcp += 1
#            print >> out, uid
        elif val == 'CNXML Document':
            cdoc += 1
#            print >> out, uid
        elif 'portal_factory' in uid:
            pfactory += 1
#            print >> out, uid
        else:
            try:
                ob = self.unrestrictedTraverse(uid)
            except Exception, msg:
                print >>out, msg
                stale += 1
    print >> out, '# indexes: ', len(catalog.indexes)
    print >> out, 'total objects: ', len(catalog.uids)
    print >> out, '  PublishedContentPointer: ', pcp
    print >> out, '  CNXML Document: ', cdoc
    print >> out, '  portal_factory: ', pfactory
    print >> out, '  stale: ', stale
    return out.getvalue()


def modifyCatalog(self):
    out = StringIO()

    cat = self.portal_catalog
    existing_indexes = cat.indexes()
    keep_indexes = ['Creator', 'portal_type', 'allowedRolesAndUsers', 'orig_id', 'review_state',
                    'path', 'getObjPositionInParent', 'sortable_title', 'modified', 'created',
                    'Date', 'effectiveRange']

    for i in keep_indexes:
        existing_indexes.remove(i)

    cat.manage_delIndex(existing_indexes)

    catalog = cat._catalog
    idx = catalog.schema['portal_type']

    print >> out, 'total: ', len(catalog.uids)

    content = []
    for uid, rid in catalog.uids.items():
        val = catalog.data[rid][idx]
        if val in  ['CNXML Document','PublishedContentPointer']:
            content.append(uid)
        elif 'portal_factory' in uid:
            content.append(uid)
    
    for uid in content:
        catalog.uncatalogObject(uid)

    print >> out, len(content)
    return out.getvalue()
