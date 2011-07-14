from Products.RhaptosCatFixes import logger
from Products.CMFPlone.PloneTool import *
from Products.CMFCore.interfaces.DublinCore import DublinCore, MutableDublinCore
from Products.CMFCore.interfaces.Discussions import Discussable
from Products.CMFCore.utils import getToolByName


def editMetadata(self
                     , obj
                     , allowDiscussion=None
                     , title=None
                     , subject=None
                     , description=None
                     , contributors=None
                     , effective_date=None
                     , expiration_date=None
                     , format=None
                     , language=None
                     , rights=None
                     ,  **kwargs):
    """Responsible for setting metadata on a content object.

    We assume the obj implements IDublinCoreMetadata.
    """
    mt = getToolByName(self, 'portal_membership')
    if not mt.checkPermission(ModifyPortalContent, obj):
        # FIXME: Some scripts rely on this being string?
        raise Unauthorized

    REQUEST = self.REQUEST
    pfx = self.field_prefix

    def getfield(request, name, default=None, pfx=pfx):
        return request.form.get(pfx + name, default)

    def tuplify(value):
        return tuple(filter(None, value))

    if DublinCore.isImplementedBy(obj):
        if title is None:
            title = getfield(REQUEST, 'title')
        if description is None:
            description = getfield(REQUEST, 'description')
        if subject is None:
            subject = getfield(REQUEST, 'subject')
        if subject is not None:
            subject = tuplify(subject)
        if contributors is None:
            contributors = getfield(REQUEST, 'contributors')
        if contributors is not None:
            contributors = tuplify(contributors)
        if effective_date is None:
            effective_date = getfield(REQUEST, 'effective_date')
        if effective_date == '':
            effective_date = 'None'
        if expiration_date is None:
            expiration_date = getfield(REQUEST, 'expiration_date')
        if expiration_date == '':
            expiration_date = 'None'

    if Discussable.isImplementedBy(obj) or \
        getattr(obj, '_isDiscussable', None):
        disc_tool = getToolByName(self, 'portal_discussion')
        if allowDiscussion is None:
            allowDiscussion = disc_tool.isDiscussionAllowedFor(obj)
            if not safe_hasattr(obj, 'allow_discussion'):
                allowDiscussion = None
            allowDiscussion = REQUEST.get('allowDiscussion', allowDiscussion)
        if type(allowDiscussion) == StringType:
            allowDiscussion = allowDiscussion.lower().strip()
        if allowDiscussion == 'default':
            allowDiscussion = None
        elif allowDiscussion == 'off':
            allowDiscussion = 0
        elif allowDiscussion == 'on':
            allowDiscussion = 1
        disc_tool.overrideDiscussionFor(obj, allowDiscussion)

    if MutableDublinCore.isImplementedBy(obj):
        if title is not None:
            obj.setTitle(title)
        if description is not None:
            obj.setDescription(description)
        if subject is not None:
            obj.setSubject(subject)
        if contributors is not None:
            obj.setContributors(contributors)
        if effective_date is not None:
            obj.setEffectiveDate(effective_date)
        if expiration_date is not None:
            obj.setExpirationDate(expiration_date)
        if format is not None:
            obj.setFormat(format)
        if language is not None:
            obj.setLanguage(language)
        if rights is not None:
            obj.setRights(rights)
        # Make the catalog aware of changes
        obj.reindexObject(idxs=kwargs.get('updateIndexes', ()))


PloneTool.editMetadata.func_code = editMetadata.func_code 
logger.info('patched %s', str(PloneTool.editMetadata))


def handleContentishEvent(ob, event):
    """ Event subscriber for (IContentish, IObjectEvent) events.
    """
    from zope.app.container.interfaces import IObjectRemovedEvent

    if IObjectAddedEvent.providedBy(event):
        if event.newParent is not None:
            ob.indexObject()

    elif IObjectClonedEvent.providedBy(event):
        ob.notifyWorkflowCreated()

    elif IObjectRemovedEvent.providedBy(event):
        ob.unindexObject()

    elif IObjectMovedEvent.providedBy(event):
        if event.newParent is not None:
            uid = getattr(ob, '_v_old_path', None)
            if uid is not None:
                new_uid = '/'.join(ob.getPhysicalPath())
                #print 'moved from', uid
                del ob._v_old_path
                catalog = getToolByName(ob, 'portal_catalog')._catalog
                index = catalog.uids.get(uid)
                if index is not None:
                    catalog.uids[new_uid] = index
                    catalog.paths[index] = new_uid
                    del catalog.uids[uid]

                    ob.reindexObject(idxs=(
                        'modified', 'allowedRolesAndUsers', 'effective',
                        'effectiveRange', 'expires', 'getId', 'id',
                        'lastModified', 'path', 'Date', 'review_state'))
                    return

            ob.indexObject()

    elif IObjectWillBeMovedEvent.providedBy(event):
        if event.oldParent is not None:
            try:
                ob._v_old_path = '/'.join(ob.getPhysicalPath())
            except:
                ob.unindexObject()


from Products.CMFCore import CMFCatalogAware
CMFCatalogAware.handleContentishEvent.func_code = handleContentishEvent.func_code
logger.info('patched %s', str(CMFCatalogAware.handleContentishEvent))
