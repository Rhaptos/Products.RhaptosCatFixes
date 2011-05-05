from StringIO import StringIO
from transaction import commit

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

    if existing_indexes:
        cat.manage_delIndex(existing_indexes)
        print >> out, 'Deleted indexes'
        commit()

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
    
    bad = 0
    todel = len(content)
    deleted = 0

    for i,uid in enumerate(content):
        try:
            catalog.uncatalogObject(uid)
            deleted += 1
        except:
            bad += 1
            pass
        if deleted % 100 == 0:
            commit()

    print >> out, 'to delete: ', todel
    print >> out, 'deleted: ', deleted
    print >> out, 'bad: ', bad
    return out.getvalue()
