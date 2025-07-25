# -*- coding: utf-8 -*-
"""
Data provider for Tagesschau

SPDX-License-Identifier: MIT
"""

# pylint: disable=too-many-lines,line-too-long
import json
import time
from ckfw.webResource import WebResource
from ckfw.params import Params


class DpZdfHeute(object):
    """
    DpZdfHeute

    """

    def __init__(self, pAddon):
        self.addon = pAddon
        self.logger = self.addon.createLogger('DpZdfHeute')
        self.starttime = time.time()

    def loadData(self):
        #
        resultArray = []
        #
        # self.kodiPG = PG.KodiProgressDialog()
        # self.kodiPG.create(30102)
        #
        dn = WebResource(self.addon, 'https://zdf-prod-futura.zdf.de/news/tv-page')
        dataString = dn.retrieveAsString()
        data = json.loads(dataString)
        #
        data = data.get('stage')
        data = data.get('teaser')
        for channel in data:
            dataModel = Params()
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
        dn = WebResource(self.addon, pUrl)
        dataString = dn.retrieveAsString()
        data = json.loads(dataString)
        #
        modules = data.get('module')
        for module in modules:
            teasers = module.get('teaser')
            for teaser in teasers:
                dataModel = Params()
                dataModel.channel = 'ZDF'
                dataModel.id = teaser.get('id')
                dataModel.title = teaser.get('title')
                dataModel.description = teaser.get('description')
                dataModel.aired = self._extractDate(teaser)
                dataModel.image = self._extractImage(teaser)
                dataModel.urlAdaptive = self._extractVideo(teaser);
                dataModel.url = dataModel.urlAdaptive
                if teaser.get('video') is not None:
                    dataModel.duration = teaser.get('video').get('duration')
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
        dn = WebResource(self.addon, 'https://zdf-prod-futura.zdf.de/news/tv-page')
        dataString = dn.retrieveAsString()
        data = json.loads(dataString)
        #
        data = data.get('module')
        data = data[0].get('teaser')
        for channel in data:
            dataModel = Params()
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

    ## https://zdf-prod-futura.zdf.de/news/abo-brands
    ## https://zdf-prod-futura.zdf.de/news/start-page
    
    def _loadMore(self):
                #
        dn = WebResource(self.addon, 'https://zdf-prod-futura.zdf.de/news/start-page')
        dataString = dn.retrieveAsString()
        data = json.loads(dataString)
        #
        data = data.get('navigation')
        data = data.get('menuItems')
        for menuItem in data:
            dataModel = Params()
            dataModel.channel = 'ZDF'
            dataModel.id = menuItem.get('id')
            dataModel.title = menuItem.get('title')
            dataModel.aired = self._extractDate(menuItem)
            dataModel.url = menuItem.get('url')

    def loadVideoUrl(self, pUrl):
        dn = WebResource(self.addon, pUrl, {'Api-Auth':'Bearer 20c238b5345eb428d01ae5c748c5076f033dfcc7'})
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
                    imageKey = list(rootElement.get('teaserImage').get('layouts').keys())[-1] 
                    image = rootElement.get('teaserImage').get('layouts').get(imageKey)
        self.logger.debug('_extractImage found {}',image)
        return image
    
    def _extractVideo(self, rootElement):
        self.logger.debug('_extractVideo from {}',rootElement)
        videourl = ''
        if rootElement.get('video') is not None:
            if rootElement.get('video').get('streamApiUrlIOS') is not None:
                videourl = rootElement.get('video').get('streamApiUrlIOS')
            elif rootElement.get('video').get('streamApiUrlAndroid') is not None:
                videourl = rootElement.get('video').get('streamApiUrlAndroid')
            elif rootElement.get('video').get('streamApiUrlVoice') is not None:
                videourl = rootElement.get('video').get('streamApiUrlVoice')
        self.logger.debug('_extractVideo found {}',videourl)
        return videourl;

    def _extractDate(self, rootElement):
        dt = '1970-01-01 00:00:00'
        if rootElement.get('editorialDate') is not None:
            if len(rootElement.get('editorialDate')) > 0:
                dt = rootElement.get('editorialDate')[0:19].replace('T', ' ')
        return dt;
