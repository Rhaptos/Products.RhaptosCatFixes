# Change uid generation process to fix ConflictError

import random
import BTrees

from Products.RhaptosCatFixes import logger
from Products.CMFCore.utils import getToolByName
from Products.CMFUid.UniqueIdHandlerTool import UniqueIdHandlerTool

UniqueIdHandlerTool._v_nextid = None
UniqueIdHandlerTool._randrange = random.randrange
UniqueIdHandlerTool._family = BTrees.family32

def register(self, obj):
    uid = self.queryUid(obj, default=None)
    if uid is None:
        # generate a new unique id and set it
        catalog = getToolByName(self, 'portal_catalog')
        if not self.UID_ATTRIBUTE_NAME in catalog._catalog.indexes:
            if self._v_nextid is None:
                self._v_nextid = self._randrange(0, self._family.maxint)
            uid = self._v_nextid
            self._v_nextid += 1
            self._setUid(obj, uid)
            return uid

        while True:
            if self._v_nextid is None:
                self._v_nextid = self._randrange(0, self._family.maxint)
            uid = self._v_nextid
            self._v_nextid += 1

            result = self.queryObject(uid)
            if result is None:
                self._setUid(obj, uid)
                return uid

            self._v_nextid = None

    return uid

UniqueIdHandlerTool.register = register
logger.info("ConflictError fix: patching UniqueIdHandlerTool.register()")
