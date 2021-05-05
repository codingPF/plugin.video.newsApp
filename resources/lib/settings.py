# -*- coding: utf-8 -*-
"""
The addon settings module
SPDX-License-Identifier: MIT
"""

# -- Imports ------------------------------------------------
import resources.lib.utils as pyUtiles
import xbmc
import xbmcvfs


# -- Classes ------------------------------------------------
class Settings(object):
    """ The settings class """

    def __init__(self, pAddonClass):
        xbmc.log("SettingsKodi:init", xbmc.LOGDEBUG)
        self._addonClass = pAddonClass
        pass

    # self.datapath
    def getDatapath(self):
        if self.getKodiVersion() > 18:
            return pyUtiles.py2_decode(xbmcvfs.translatePath(self._addonClass.getAddonInfo('profile')))
        else:
            return pyUtiles.py2_decode(xbmc.translatePath(self._addonClass.getAddonInfo('profile')))

    def getKodiVersion(self):
        """
        Get Kodi major version
        Returns:
            int: Kodi major version (e.g. 18)
        """
        xbmc_version = xbmc.getInfoLabel("System.BuildVersion")
        return int(xbmc_version.split('-')[0].split('.')[0])

    # General
    def isUseZdf(self):
        return self._addonClass.getSetting('useZDF') == 'true'

    def isUseArd(self):
        return self._addonClass.getSetting('useARD') == 'true'
