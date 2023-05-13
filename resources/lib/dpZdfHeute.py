# -*- coding: utf-8 -*-
"""
Data provider for Tagesschau

SPDX-License-Identifier: MIT
"""

# pylint: disable=too-many-lines,line-too-long
import json
import time

import resources.lib.appContext as appContext
import resources.lib.webResource as WebResource
import resources.lib.ui.episodeModel as EpisodeModel


class DpZdfHeute(object):
    """
    DpZdfHeute

    """

    def __init__(self):
        self.logger = appContext.LOGGER.getInstance('DpTdfHeute')
        self.settings = appContext.SETTINGS
        self.starttime = time.time()

    def run(self):
        #
        if not(self.db.isInitialized()):
            self.settings.setLastUpdateIndex('0')
            self.db.create()
        #
        self.loadcategory()
        #
    
    def loadData(self):
        #
        resultArray = []
        #
        # self.kodiPG = PG.KodiProgressDialog()
        # self.kodiPG.create(30102)
        #
        dn = WebResource.WebResource('https://zdf-heute-cdn.live.cellular.de/news/tv-page')
        dataString = dn.retrieveAsString()
        data = json.loads(dataString)
        #
        data = data.get('stage')
        data = data.get('teaser')
        for channel in data:
            dataModel = EpisodeModel.EpisodeModel()
            dataModel.channel = 'ZDF'
            dataModel.id = channel.get('id')
            dataModel.title = channel.get('title')
            dataModel.aired = self._extractDate(channel)
            dataModel.image = self._extractImage(channel)
            dataModel.urlAdaptive = self._extractVideo(channel);
            dataModel.url = dataModel.urlAdaptive
            dataModel.mode = 'playZdfItem'
            if channel.get('video') is not None:
                dataModel.duration = channel.get('video').get('duration')
            #
            resultArray.append(dataModel)
            #
        return resultArray

    def loadBroadcasts(self, pUrl):
        #
        resultArray = []
        #
        # self.kodiPG = PG.KodiProgressDialog()
        # self.kodiPG.create(30102)
        #
        dn = WebResource.WebResource(pUrl)
        dataString = dn.retrieveAsString()
        data = json.loads(dataString)
        #
        data = data.get('module')
        data = data[0].get('teaser')
        for channel in data:
            dataModel = EpisodeModel.EpisodeModel()
            dataModel.channel = 'ZDF'
            dataModel.id = channel.get('id')
            dataModel.title = channel.get('title')
            dataModel.description = channel.get('description')
            dataModel.aired = self._extractDate(channel)
            dataModel.image = self._extractImage(channel)
            dataModel.urlAdaptive = self._extractVideo(channel);
            dataModel.url = dataModel.urlAdaptive
            if channel.get('video') is not None:
                dataModel.duration = channel.get('video').get('duration')
            #
            resultArray.append(dataModel)
            #
        return resultArray

    def loadShows(self):
        #
        resultArray = []
        #
        # self.kodiPG = PG.KodiProgressDialog()
        # self.kodiPG.create(30102)
        #
        dn = WebResource.WebResource('https://zdf-heute-cdn.live.cellular.de/news/tv-page')
        dataString = dn.retrieveAsString()
        data = json.loads(dataString)
        #
        data = data.get('module')
        data = data[0].get('teaser')
        for channel in data:
            dataModel = EpisodeModel.EpisodeModel()
            dataModel.channel = 'ZDF'
            dataModel.id = channel.get('id')
            dataModel.title = channel.get('title')
            dataModel.aired = self._extractDate(channel)
            dataModel.image = self._extractImage(channel)
            dataModel.url = channel.get('url')
            #
            resultArray.append(dataModel)
            #
        return resultArray

    ## https://zdf-heute-cdn.live.cellular.de/news/abo-brands
    ## https://zdf-heute-cdn.live.cellular.de/news/start-page
    
    def _loadMore(self):
                #
        dn = WebResource.WebResource('https://zdf-heute-cdn.live.cellular.de/news/start-page')
        dataString = dn.retrieveAsString()
        data = json.loads(dataString)
        #
        data = data.get('navigation')
        data = data.get('menuItems')
        for menuItem in data:
            dataModel = EpisodeModel.EpisodeModel()
            dataModel.channel = 'ZDF'
            dataModel.id = menuItem.get('id')
            dataModel.title = menuItem.get('title')
            dataModel.aired = self._extractDate(menuItem)
            dataModel.url = menuItem.get('url')

    def loadVideoUrl(self, pUrl):
        dn = WebResource.WebResource(pUrl, {'Api-Auth':'Bearer 20c238b5345eb428d01ae5c748c5076f033dfcc7'})
        dataString = dn.retrieveAsString()
        data = json.loads(dataString)
        #
        urlsAdaptive = []
        urlsMp4 = []
        for prio in data.get('priorityList'):
            for formitaeten in prio.get('formitaeten'):
                if (formitaeten.get('mimeType') == 'application/x-mpegURL'):
                    url = self.extractValue(formitaeten, 'qualities', 0, 'audio', 'tracks', 0, 'uri')
                    if (url is not None):
                        urlsAdaptive.append(url)
                if (formitaeten.get('mimeType') == 'video/mp4'):
                    url = self.extractValue(formitaeten, 'qualities', 0, 'audio', 'tracks', 0, 'uri')
                    if (url is not None):
                        urlsMp4.append(url)
        return {'adaptive': urlsAdaptive, 'mp4': urlsMp4}



    def extractValue(self, rootElement, *args):
        root = rootElement;
        for searchPath in args:
            if root is None:
                return None
            elif isinstance(root, list):
                root = root[searchPath]
            else:
                root = root.get(searchPath)
        return root;

    def _extractImage(self, rootElement):
        self.logger.debug('_extractImage from {}',rootElement)
        image = ''
        if rootElement.get('teaserImage') is not None:
            if rootElement.get('teaserImage').get('layouts') is not None:
                if rootElement.get('teaserImage').get('layouts').get('original') is not None:
                    image = rootElement.get('teaserImage').get('layouts').get('original')
                elif len(list(rootElement.get('teaserImage').get('layouts').keys())) > 0:
                    image = list(rootElement.get('teaserImage').get('layouts').keys())[-1]
        return image
    
    def _extractVideo(self, rootElement):
        videourl = ''
        if rootElement.get('video') is not None:
            if rootElement.get('video').get('streamApiUrlIOS') is not None:
                videourl = rootElement.get('video').get('streamApiUrlIOS')
            elif rootElement.get('video').get('streamApiUrlAndroid') is not None:
                videourl = rootElement.get('video').get('streamApiUrlAndroid')
            elif len(list(rootElement.get('video').keys())) > 0:
                videourl = list(rootElement.get('video').keys())[-1]
        return videourl;

    def _extractDate(self, rootElement):
        dt = '1970-01-01 00:00:00'
        if rootElement.get('editorialDate') is not None:
            if len(rootElement.get('editorialDate')) > 0:
                dt = rootElement.get('editorialDate')[0:19].replace('T', ' ')
        return dt;
