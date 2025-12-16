# -*- coding: utf-8 -*-
"""
The main addon module

SPDX-License-Identifier: MIT

"""
from ckfw.kodi import Kodi
from ckfw.kodiUi import KodiUI
from ckfw import utils as pyUtils
from .dpTagesschau import DpTagesschau
from .dpZdfHeute import DpZdfHeute
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
            vLinks = DpZdfHeute(self).loadVideoUrl(tgtUrl)
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
            vLinks = DpTagesschau(self).loadEpisode(tgtUrl)
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
        elif mode == 'ARDArchive':
            self._generateARDArchive(self.getParameters('date'))
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
        dataArray.extend(DpTagesschau(self).loadShows())
        from datetime import date, timedelta
        last_three_dates = [
            (date.today() - timedelta(days=i)).isoformat()
            for i in range(3)
        ]

        ui = KodiUI(self)
        for d in last_three_dates:
            ui.addDirectoryItem(pTitle='Archive ' + d, pUrl=self.generateUrl({'mode': "ARDArchive", 'date':d}), pIcon='https://upload.wikimedia.org/wikipedia/commons/0/06/Tagesschau.de_logo.svg')

        ui.addItems(dataArray,'play')
        #
        ui.render()

    # generate all episodes for a ZDF show
    def _generateZdfEntity(self, pUrl):
        self.logger.debug('_generateZdfEntity')
        dataArray = []
        dataArray.extend(DpZdfHeute(self).loadBroadcasts(pUrl))
        ui = KodiUI(self)
        ui.addItems(dataArray, 'playZdfItem')
        ui.render()
    
    # generate all ZDF shows
    def _generateZdfFolder(self):
        self.logger.debug('_generateZdfFolder')
        dataArray = []
        dataArray.extend(DpZdfHeute(self).loadShows())
        ui = KodiUI(self)
        ui.addDirectories(dataArray,'zdfEntity')
        ui.render()
        self.setViewId(self.resolveViewId('THUMBNAIL'))

    # ARD Archive
    def _generateARDArchive(self, pDate):
        self.logger.debug('_generateARDArchive')
        dataArray = []
        dataArray.extend(DpTagesschau(self).loadArchive(pDate))
        ui = KodiUI(self)
        ui.addItems(dataArray,'play')
        ui.render()

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
            dataArray.extend(DpTagesschau(self).loadData())
            #
            ardFolderUrl = self.generateUrl({'mode': "ardFolder"})
            ardIcon = pyUtils.createPath((self.getAddonPath(), 'resources', 'icons', 'ard.png'))
            ui.addDirectoryItem(pTitle='ARD', pUrl=ardFolderUrl, pIcon=ardIcon)
        #
        if self.isUseZdf():
            dataArray.extend(DpZdfHeute(self).loadData())
            #
            zdfFolderUrl = self.generateUrl({'mode': "zdfFolder"})
            zdfIcon = pyUtils.createPath((self.getAddonPath(), 'resources', 'icons', 'zdf.png'))
            ui.addDirectoryItem(pTitle='ZDF', pUrl=zdfFolderUrl, pIcon=zdfIcon)
        #
        dataArray = sorted(dataArray, key=lambda d: d.aired, reverse=True) 
        #
        ui.addItems(dataArray)
        ui.render()
