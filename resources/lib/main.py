# -*- coding: utf-8 -*-
"""
The main addon module

SPDX-License-Identifier: MIT

"""
import resources.lib.appContext as appContext
from resources.lib.kodi import Kodi
from resources.lib.kodiUi import KodiUI
import resources.lib.dpTagesschau as DpTagesschau
import resources.lib.dpZdfHeute as DpZdfHeute
import resources.lib.utils as pyUtils


#
class Main(Kodi):

    def __init__(self):
        super(Main, self).__init__()
        self.logger = appContext.LOGGER.getInstance('MAIN')
        self.settings = appContext.SETTINGS
        #

    def run(self):
        #
        mode = self.getParameters('mode')
        parameterId = self.getParameters('id')
        self.logger.info('Run Plugin with Parameters {}', self.getParameters())
        if mode == 'playZdfItem':
            tgtUrl = pyUtils.b64decode(self.getParameters('urlB64'))
            self.logger.debug('resolve target url for ZDF {}', tgtUrl)
            vLinks = DpZdfHeute.DpZdfHeute().loadVideoUrl(tgtUrl)
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
            vLinks = DpTagesschau.DpTagesschau().loadEpisode(tgtUrl)
            self.playItem(vLinks)
            #
        elif mode == 'download':
            #
            rs = self.db.getEpisode(parameterId)
            url = rs[0][5]
            name = rs[0][1]
            name = pyUtils.file_cleanupname(name)
            fullName = pyUtils.createPath((self.translatePath(self.settings.getDownloadPath()), name))
            pyUtils.url_retrieve(url, fullName, reporthook=kodiPG.update, chunk_size=65536, aborthook=self.getAbortHook())
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

    # Processors
    
    # generate all ARD episodes from news
    def _generateArdFolder(self):
        self.logger.debug('_generateArdFolder')
        dataArray = []
        dataArray.extend(DpTagesschau.DpTagesschau().loadShows())
        ui = KodiUI(self)
        ui.addItems(dataArray,'play')
        ui.render()

    # generate all episodes for a ZDF show
    def _generateZdfEntity(self, pUrl):
        self.logger.debug('_generateZdfEntity')
        dataArray = []
        dataArray.extend(DpZdfHeute.DpZdfHeute().loadBroadcasts(pUrl))
        ui = KodiUI(self)
        ui.addItems(dataArray, 'playZdfItem')
        ui.render()
    
    # generate all ZDF shows
    def _generateZdfFolder(self):
        self.logger.debug('_generateZdfFolder')
        dataArray = []
        dataArray.extend(DpZdfHeute.DpZdfHeute().loadShows())
        ui = KodiUI(self, pViewId=self.resolveViewId('THUMBNAIL'))
        ui.addDirectories(dataArray,'zdfEntity')
        ui.render()

    # generate top level menu
    # Folder for ARD and ZDF
    # plus items for all top level episodes for this day
    def _generateTopNewsList(self):
        self.logger.debug('_generateTopNewsList')
        self.logger.debug('Settings: isUseArd "{}" isUseZdf "{}" type of {}', self.settings.isUseArd(), self.settings.isUseZdf(), type(self.settings.isUseArd()));
        dataArray = []
        ui = KodiUI(self)
        #
        if self.settings.isUseArd():
            dataArray.extend(DpTagesschau.DpTagesschau().loadData())
            #
            ardFolderUrl = self.generateUrl({'mode': "ardFolder"})
            ardIcon = pyUtils.createPath((self.getAddonPath(), 'resources', 'icons', 'ard.png'))
            ui.addDirectoryItem(pTitle='ARD', pUrl=ardFolderUrl, pIcon=ardIcon)
        #
        if self.settings.isUseZdf():
            dataArray.extend(DpZdfHeute.DpZdfHeute().loadData())
            #
            zdfFolderUrl = self.generateUrl({'mode': "zdfFolder"})
            zdfIcon = pyUtils.createPath((self.getAddonPath(), 'resources', 'icons', 'zdf.png'))
            ui.addDirectoryItem(pTitle='ZDF', pUrl=zdfFolderUrl, pIcon=zdfIcon)
        #
        dataArray = sorted(dataArray, key=lambda d: d.aired, reverse=True) 
        #
        ui.addItems(dataArray)
        ui.render()
