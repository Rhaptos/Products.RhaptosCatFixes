# prevent writing to zodb on each user login
# each time user login to site plone makes changes in zodb

from Products.RhaptosCatFixes import logger
from Products.CMFPlone.MembershipTool import MembershipTool


def setLoginTimes(self):
    res=False
    if not self.isAnonymousUser():
        member = self.getAuthenticatedMember()
        login_time = member.getProperty('login_time', '2000/01/01')
        if str(login_time) == '2000/01/01':
            res=True
            login_time = self.ZopeTime()

        time = self.ZopeTime()
        if not res and (time - login_time) < 0.1:
            return False

        member.setProperties(login_time=time, last_login_time=login_time)
    return res

MembershipTool.setLoginTimes = setLoginTimes
logger.info("Patching MembershipTool.setLoginTimes()")
