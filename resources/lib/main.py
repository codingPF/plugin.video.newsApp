# -*- coding: utf-8 -*-
"""
The main addon module

SPDX-License-Identifier: MIT

"""
import resources.lib.appContext as appContext
from resources.lib.kodi import Kodi
import resources.lib.dpTagesschau as DpTagesschau
import resources.lib.dpZdfHeute as DpZdfHeute
import resources.lib.ui.episodeUi as EpisodeUI
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
        if mode == 'play':
            tgtUrl = pyUtils.b64decode(self.getParameters('urlB64'))
            if self.getParameters('channel') == 'ZDF':
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
            else:
                self.logger.info('Play Url {}', tgtUrl)
                self.playItem(tgtUrl)

        elif mode == 'download':
            #
            rs = self.db.getEpisode(parameterId)
            url = rs[0][5]
            name = rs[0][1]
            name = pyUtils.file_cleanupname(name)
            fullName = pyUtils.createPath((self.translatePath(self.settings.getDownloadPath()), name))
            pyUtils.url_retrieve(url, fullName, reporthook=kodiPG.update, chunk_size=65536, aborthook=self.getAbortHook())
            #
        else:
            dataArray = []
            self.logger.debug('Settings: isUseArd "{}" isUseZdf "{}" type of {}', self.settings.isUseArd(), self.settings.isUseZdf(), type(self.settings.isUseArd()));
            if self.settings.isUseArd():
                dataArray.extend(DpTagesschau.DpTagesschau().loadData())
            if self.settings.isUseZdf():
                dataArray.extend(DpZdfHeute.DpZdfHeute().loadData())
            ui = EpisodeUI.EpisodeUI(self)
            ui.generate(dataArray)
        #
