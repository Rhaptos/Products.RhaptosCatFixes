from StringIO import StringIO

def checkCatalog(self):
    out = StringIO()
    catalog = self.portal_catalog._catalog

    stale = 0
    pfactory = 0
    for uid in catalog.uids.keys():
	if 'portal_factory' in uid:
	    pfactory += 1
	    print >> out, uid
	else:
	    try:
	        ob = self.unrestrictedTraverse(uid)
	    except Exception, msg:
	        print >>oud, msg
	        stale += 1

    print >> out, 'total: ', len(catalog.uids)
    print >> out, 'portal_factory: ', pfactory
    print >> out, 'stale: ', stale
    return out.getvalue()


def modifyCatalog(self):
    out = StringIO()
    catalog = self.portal_catalog._catalog
    idx = catalog.schema['portal_type']

    print >> out, 'total: ', len(catalog.uids)

    content = []
    for uid, rid in catalog.uids.items():
        val = catalog.data[rid][idx]
        if val == 'PublishedContentPointer':
    	    content.append(uid)
    	elif 'portal_factory' in uid:
    	    content.append(uid)
    
    for uid in content:
	catalog.uncatalogObject(uid)

    print >> out, len(content)
    return out.getvalue()
