# always insert IITreeSet
# this patch reduce ConflictErrors on high load sites
# for example we have 3 threads that update catalog index
# 1 and 2 thread creating new document, at this point we will get ConflictError because
# both threads inserts new value into BTree
# suppose first thread completed and thread 2 retryed and 3 thread (or 1 thread again)
# inserting new value into index
# at this point if first thread insert integer (default behaviour)
# we will get ConflictError, because second thread need to remove integer value
# and replace it with IITreeSet
# if first thread inserts IITreeSet instead integer
# in second run IITreeSet can do conflict resolution for thread 2 and thread 3

from BTrees.IIBTree import IITreeSet
from Products.PluginIndex.common.UnIndex import UnIndex
from Products.RhaptosCatFixes import logger


def insertForwardIndexEntry(self, entry, documentId):
    indexRow = self._index.get(entry, _marker)

    if indexRow is _marker:
        self._index[entry] = IITreeSet((documentId,))
        try:
            self._length.change(1)
        except AttributeError:
            if isinstance(self.__len__, BTrees.Length.Length):
                self._length = self.__len__
                del self.__len__
            self._length.change(1)
    else:
        try: indexRow.insert(documentId)
        except AttributeError:
            indexRow=IITreeSet((indexRow, documentId))
            self._index[entry] = indexRow

UnIndex.insertForwardIndexEntry = insertForwardIndexEntry
logger.info("ConflictError fix: patching PluginIndex UnIndex.insertForwardIndexEntry()")
