# fix ConflictError

import random
from Products.CNXFixes import logger
from Products.ZCTextIndex.Lexicon import Lexicon

Lexicon._v_nextid = None
Lexicon._randrange = random.randrange

def _getWordIdCreate(self, word):
    wid = self._wids.get(word)
    if wid is None:
        while True:
            if self._v_nextid is None:
                self._v_nextid = self._randrange(0x4000, 0x10000000)

            wid = self._v_nextid
            self._v_nextid += 1

            if wid not in self._words:
                break

            self._v_nextid = None

        self.length.change(1)
        self._wids[word] = wid
        self._words[wid] = word
    return wid

Lexicon._getWordIdCreate = _getWordIdCreate
logger.info("ConflictError fix: patching ZCTextIndex Lexicon._getWordIdCreate()")
