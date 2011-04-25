# fix ConflictError

import random
from Products.RhaptosCatFixes import logger
from BTrees.IIBTree import IITreeSet
from Products.ZCTextIndex.WidCode import encode
from Products.TextIndexNG2.lexicons.StandardLexicon import Lexicon
from Products.TextIndexNG2.storages import StandardStorage, StupidStorage


Lexicon._v_nextid = None
Lexicon._randrange = random.randrange

def getWordIdList(self, words):
    fw_idx = self._forward_idx
    fw_idx_get = fw_idx.get
    rev_idx = self._inverse_idx
    if self.truncate_left: lfw_idx = self._lforward_idx

    wids = []
    append = wids.append

    for word in words:
        wid = fw_idx_get(word)
        if not wid:
            while True:
                if self._v_nextid is None:
                    self._v_nextid = self._randrange(0x4000, 0x10000000)

                wid = self._v_nextid
                self._v_nextid += 1

                if wid not in rev_idx:
                    break

                self._v_nextid = None

            fw_idx[word] = wid
            rev_idx[wid] = word
            if self.truncate_left:
                lfw_idx[word[::-1]] = wid

        append(wid)
    return wids

Lexicon.getWordIdList = getWordIdList
logger.info("ConflictError fix: patching TextIndexNG2 Lexicon.insertWords()")


def StandardStorageInsert(self, wids, docid):
    if isinstance(wids, int): wids = [wids]
    idx = self._forward_idx

    for wid in wids:
        try:
            idx[wid].insert(docid)
        except KeyError:
            idx[wid] = IITreeSet((docid,))
        except:
            olddocid = idx[wid]
            idx[wid] = IITreeSet([olddocid, docid])

    if not self._reverse_idx.has_key(docid): self._length.change(1)
    self._reverse_idx[docid] = encode(wids)
    self._frequencies[docid] = self._get_frequencies(wids)


StandardStorage.Storage.insert = StandardStorageInsert


def StupidStorageInsert(self, wids, docid):
    if isinstance(wids, int): wids = [wids]
    idx = self._forward_idx

    for wid in wids:
        try:
            idx[wid].insert(docid)
        except KeyError:
            idx[wid] = IITreeSet((docid,))
        except:
            olddocid = idx[wid]
            idx[wid] = IITreeSet([olddocid, docid])

    if self._reverse_idx.has_key( docid):
        self._reverse_idx[docid].update(wids)
    else:
        self._length.change(1)
        self._reverse_idx[docid] = IITreeSet(wids)


StupidStorage.Storage.insert = StupidStorageInsert
