# This file is necessary to make this directory a package.

from Products import CacheSetup

import logging
logger = logging.getLogger("enfold.fixes")

def initialize(context):
    #try:
	#import patch 
	#patch.applyPatches()
	#logger.info("Apply portal factory fix.")
    #except:
        #pass

    # Fix setLoginTimes, prevent writing to zodb on user login
    try:
	import logintime
    except:
	pass

    # fix uid generation to prevent ConflictError
    try:
        import cmfuid
    except:
	pass

    # fix word key to prevent ConflictError
    try:
	import txng2
    except:
	pass

    # fix word key to prevent ConflictError
    try:
	import txng3
    except:
	pass

    try:
	import zctextindex
    except:
	pass

    try:
	import unindex
    except:
	pass

    try:
	import catalog
    except:
	pass
