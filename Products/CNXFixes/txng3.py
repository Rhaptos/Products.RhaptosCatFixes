# fix ConflictError

import random
from Products.CNXFixes import logger
from zopyx.txng3.core.lexicon import Lexicon
from zopyx.txng3.core.exceptions import LexiconError
from zopyx.txng3.core.config import DEFAULT_LANGUAGE


Lexicon._v_nextid = None
Lexicon._randrange = random.randrange

def insertWords(self, words, language=DEFAULT_LANGUAGE):
    tree = self._getTree(language)

    wids = []
    for word in words:
        if not isinstance(word, unicode):
            raise LexiconError('Only unicode string can be indexed (%s)' % repr(word))

        try:
            wids.append(tree[word])
        except KeyError:
            while True:
                if self._v_nextid is None:
                    self._v_nextid = self._randrange(0x4000, 0x10000000)

                wid = self._v_nextid
                self._v_nextid += 1

                if wid not in self._wids:
                    break

                self._v_nextid = None

            tree[word] = wid
            self._wids[wid] = (word, language)
            wids.append(wid)

    return wids


Lexicon.insertWords = insertWords
logger.info("ConflictError fix: patching zopyx.txng3.core.lexicon.Lexicon.insertWords()")
