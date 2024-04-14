# -*- coding: utf-8 -*-
"""
The main addon module

SPDX-License-Identifier: MIT

"""
from ckfw.kodi import Kodi
from ckfw import kodiUi as KodiUI
from . import dpTagesschau as DpTagesschau
from . import dpZdfHeute as DpZdfHeute
#
class Main(Kodi):

    def __init__(self):
        super(Main, self).__init__()
        self.logger = self.createLogger('MAIN')
        #

    def run(self):
        #
        mode = self.getParameters('mode')
        parameterId = self.getParameters('id')
        self.logger.info('Run Plugin with Parameters {}', self.getParameters())
        if mode == 'playZdfItem':
            tgtUrl = pyUtils.b64decode(self.getParameters('urlB64'))
            self.logger.debug('resolve target url for ZDF {}', tgtUrl)
            vLinks = DpZdfHeute.DpZdfHeute(self).loadVideoUrl(tgtUrl)
            self.logger.debug('VideoUrls {}', vLinks)
            if vLinks is not None:
                if (len(vLinks.get('adaptive')) > 0):
                    self.logger.debug('VideoUrls adaptive {}', vLinks.get('adaptive'))
                    tgtUrl = vLinks.get('adaptive')[0]
                elif (len(vLinks.get('mp4')) > 0):
                    self.logger.debug('VideoUrls mp4 {}', vLinks.get('mp4'))
                    tgtUrl = vLinks.get('mp4')[0]
                self.logger.info('Play Url {}', tgtUrl)
                self.playItem(tgtUrl)
        elif mode == 'play':
            tgtUrl = pyUtils.b64decode(self.getParameters('urlB64'))
            self.logger.info('Play Url {}', tgtUrl)
            self.playItem(tgtUrl)
                                
        elif mode == 'ardEpisode':
            tgtUrl = pyUtils.b64decode(self.getParameters('urlB64'))
            vLinks = DpTagesschau.DpTagesschau(self).loadEpisode(tgtUrl)
            self.playItem(vLinks)
            #
        elif mode == 'zdfFolder':
            #
            self._generateZdfFolder()
            #
        elif mode == 'zdfEntity':
            #
            tgtUrl = pyUtils.b64decode(self.getParameters('urlB64'))
            self._generateZdfEntity(tgtUrl)
            #
        elif mode == 'ardFolder':
            #
            self._generateArdFolder()
            #
        else:
            self._generateTopNewsList()

        #

    # General
    def isUseZdf(self):
        return self.getSetting('useZDF') == 'true'

    def isUseArd(self):
        return self.getSetting('useARD') == 'true'
    
    # Processors
    
    # generate all ARD episodes from news
    def _generateArdFolder(self):
        self.logger.debug('_generateArdFolder')
        dataArray = []
        dataArray.extend(DpTagesschau.DpTagesschau(self).loadShows())
        ui = KodiUI(self)
        ui.addItems(dataArray,'play')
        ui.render()

    # generate all episodes for a ZDF show
    def _generateZdfEntity(self, pUrl):
        self.logger.debug('_generateZdfEntity')
        dataArray = []
        dataArray.extend(DpZdfHeute.DpZdfHeute(self).loadBroadcasts(pUrl))
        ui = KodiUI(self)
        ui.addItems(dataArray, 'playZdfItem')
        ui.render()
    
    # generate all ZDF shows
    def _generateZdfFolder(self):
        self.logger.debug('_generateZdfFolder')
        dataArray = []
        dataArray.extend(DpZdfHeute.DpZdfHeute(self).loadShows())
        ui = KodiUI(self)
        ui.addDirectories(dataArray,'zdfEntity')
        ui.render()
        self.setViewId(self.resolveViewId('THUMBNAIL'))

    # generate top level menu
    # Folder for ARD and ZDF
    # plus items for all top level episodes for this day
    def _generateTopNewsList(self):
        self.logger.debug('_generateTopNewsList')
        self.logger.debug('Settings: isUseArd "{}" isUseZdf "{}" type of {}', self.isUseArd(), self.isUseZdf(), type(self.isUseArd()));
        dataArray = []
        ui = KodiUI(self)
        #
        if self.isUseArd():
            dataArray.extend(DpTagesschau.DpTagesschau(self).loadData())
            #
            ardFolderUrl = self.generateUrl({'mode': "ardFolder"})
            ardIcon = pyUtils.createPath((self.getAddonPath(), 'resources', 'icons', 'ard.png'))
            ui.addDirectoryItem(pTitle='ARD', pUrl=ardFolderUrl, pIcon=ardIcon)
        #
        if self.isUseZdf():
            dataArray.extend(DpZdfHeute.DpZdfHeute(self).loadData())
            #
            zdfFolderUrl = self.generateUrl({'mode': "zdfFolder"})
            zdfIcon = pyUtils.createPath((self.getAddonPath(), 'resources', 'icons', 'zdf.png'))
            ui.addDirectoryItem(pTitle='ZDF', pUrl=zdfFolderUrl, pIcon=zdfIcon)
        #
        dataArray = sorted(dataArray, key=lambda d: d.aired, reverse=True) 
        #
        ui.addItems(dataArray)
        ui.render()
