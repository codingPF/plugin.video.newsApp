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
            if channel.get('editorialDate') is not None:
                if len(channel.get('editorialDate')) > 0:
                    dataModel.aired = channel.get('editorialDate')[0:19].replace('T', ' ')
            #
            if channel.get('teaserImage') is not None:
                if channel.get('teaserImage').get('layouts') is not None:
                    dataModel.image = channel.get('teaserImage').get('layouts').get('original')
                elif channel.get('teaserImage').get('layouts') is not None:
                    dataModel.image = channel.get('teaserImage').get('layouts').get('1920x1080')
                elif channel.get('teaserImage').get('layouts') is not None:
                    dataModel.image = channel.get('teaserImage').get('layouts').get('1280x720')
            #
            if channel.get('video') is not None:
                dataModel.duration = channel.get('video').get('duration')
                videoLink = None
                if channel.get('video').get('streamApiUrlIOS') is not None:
                    videoLink = channel.get('video').get('streamApiUrlIOS')
                if channel.get('video').get('streamApiUrlAndroid') is not None:
                    videoLink = channel.get('video').get('streamApiUrlAndroid')
                dataModel.urlAdaptive = videoLink
                dataModel.url = videoLink
                """
                vLinks = self.loadVideoUrl(videoLink)
                if vLinks is not None:
                    if (len(vLinks.get('adaptive')) > 0):
                        dataModel.urlAdaptive = vLinks.get('adaptive')[0]
                    if (len(vLinks.get('mp4')) > 0):
                        dataModel.url = vLinks.get('mp4')[0]
                """
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
            if channel.get('editorialDate') is not None:
                if len(channel.get('editorialDate')) > 0:
                    dataModel.aired = channel.get('editorialDate')[0:19].replace('T', ' ')
            #
            if channel.get('teaserImage') is not None:
                if channel.get('teaserImage').get('layouts') is not None:
                    dataModel.image = channel.get('teaserImage').get('layouts').get('original')
                elif channel.get('teaserImage').get('layouts') is not None:
                    dataModel.image = channel.get('teaserImage').get('layouts').get('1920x1080')
                elif channel.get('teaserImage').get('layouts') is not None:
                    dataModel.image = channel.get('teaserImage').get('layouts').get('1280x720')
            #
            if channel.get('video') is not None:
                dataModel.duration = channel.get('video').get('duration')
                videoLink = None
                if channel.get('video').get('streamApiUrlIOS') is not None:
                    videoLink = channel.get('video').get('streamApiUrlIOS')
                if channel.get('video').get('streamApiUrlAndroid') is not None:
                    videoLink = channel.get('video').get('streamApiUrlAndroid')
                dataModel.urlAdaptive = videoLink
                dataModel.url = videoLink
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
            if channel.get('editorialDate') is not None:
                if len(channel.get('editorialDate')) > 0:
                    dataModel.aired = channel.get('editorialDate')[0:19].replace('T', ' ')
            #
            if channel.get('teaserImage') is not None:
                if channel.get('teaserImage').get('layouts') is not None:
                    dataModel.image = channel.get('teaserImage').get('layouts').get('original')
                elif channel.get('teaserImage').get('layouts') is not None:
                    dataModel.image = channel.get('teaserImage').get('layouts').get('1920x1080')
                elif channel.get('teaserImage').get('layouts') is not None:
                    dataModel.image = channel.get('teaserImage').get('layouts').get('1280x720')
            #
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
            if menuItem.get('editorialDate') is not None:
                if len(menuItem.get('editorialDate')) > 0:
                    dataModel.aired = menuItem.get('editorialDate')[0:19].replace('T', ' ')
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
