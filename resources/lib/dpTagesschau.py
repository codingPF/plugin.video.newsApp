# -*- coding: utf-8 -*-
"""
Data provider for Tagesschau

SPDX-License-Identifier: MIT
"""

# pylint: disable=too-many-lines,line-too-long
import json
import time
import datetime
import resources.lib.appContext as appContext
import resources.lib.webResource as WebResource
import resources.lib.ui.episodeModel as EpisodeModel


class DpTagesschau(object):
    """
    DpTagesschau

    """

    def __init__(self):
        self.logger = appContext.LOGGER.getInstance('DpTagesschau')
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
        self.logger.debug('loadData')
        dn = WebResource.WebResource('https://www.tagesschau.de/api2u/channels')
        dataString = dn.retrieveAsString()
        data = json.loads(dataString)
        #
        data = data.get('channels')
        for channel in data:
            dataModel = EpisodeModel.EpisodeModel()
            dataModel.channel = 'ARD'
            dataModel.id = channel.get('sophoraId')
            dataModel.title = channel.get('title')
            dataModel.aired = self._extractDate(channel)
            dataModel.image = self._extractImage(channel)
            dataModel.url = self._extractVideo(channel)
            dataModel.urlAdaptive = dataModel.url
            dataModel.mode = 'play'
            #
            startTime = channel.get('start')
            endTime = channel.get('end')
            if dataModel.title.startswith('Aktuelle Sendung: Tagesthemen') and startTime is not None and endTime is not None:
                dataModel.urlAdaptive = dataModel.urlAdaptive + '?start={}&end={}'.format(startTime, (startTime+1000)) #??
                self.logger.debug('Aktuelle Sendung {}',dataModel.urlAdaptive)
                self.logger.debug('Aktuelle Sendung Times start {} end {}',startTime,endTime)
                dataModel.aired = datetime.datetime.fromtimestamp(startTime).isoformat()
            elif dataModel.title.startswith('Aktuelle Sendung') and startTime is not None and endTime is not None:
                dataModel.urlAdaptive = dataModel.urlAdaptive + '?start={}&end={}'.format(startTime, endTime)
                self.logger.debug('Aktuelle Sendung Times start {} end {}',startTime,endTime)
                self.logger.debug('Aktuelle Sendung {}',dataModel.urlAdaptive)
                dataModel.aired = datetime.datetime.fromtimestamp(startTime).isoformat()
            #
            resultArray.append(dataModel)
            #
        return resultArray

    def loadEpisode(self, pUrl):
        self.logger.debug('loadEpisode for {}', pUrl)
        dn = WebResource.WebResource(pUrl)
        dataString = dn.retrieveAsString()
        data = json.loads(dataString)
        url = ''
        for mediadata in data.get('fullvideo')[0].get('mediadata'):
            if 'h264s' in mediadata:
                url = mediadata.get('h264s')
            if 'h264m' in mediadata:
                url = mediadata.get('h264m')
            if 'h264l' in mediadata:
                url = mediadata.get('h264l')
            if 'h264xl' in mediadata:
                url = mediadata.get('h264xl')
            if 'podcastvideom' in mediadata:
                url = mediadata.get('podcastvideom')
            if 'adaptivestreaming' in mediadata:
                url = mediadata.get('adaptivestreaming')
        self.logger.debug('loadEpisode resolved to {}', url)
        return url


    def loadShows(self):
        #
        resultArray = []
        #
        self.logger.debug('loadShows')
        dn = WebResource.WebResource('https://www.tagesschau.de/api2u/news')
        dataString = dn.retrieveAsString()
        # load all top show urls to have the index page for all episodes
        data = json.loads(dataString)
        for entry in data.get('news'):            
            if entry.get('type') == 'video':
                dataModel = EpisodeModel.EpisodeModel()
                dataModel.channel = 'ARD'
                dataModel.id = entry.get('sophoraId')
                dataModel.title = entry.get('title')
                dataModel.aired = self._extractDate(entry)
                dataModel.url = self._extractVideo(entry)
                dataModel.image = self._extractImage(entry)
                self.logger.debug('add image for {} {}',dataModel.title,dataModel.image)             
                resultArray.append(dataModel)
            #
        return resultArray

    def loadBroadcasts(self, pUrl):
        #
        resultArray = []
        #
        self.logger.debug('loadBroadcasts')
        dn = WebResource.WebResource(pUrl)
        dataString = dn.retrieveAsString()
        data = json.loads(dataString)
        data = data.get('latestBroadcastsPerType')
        for entry in data:
            dataModel = EpisodeModel.EpisodeModel()
            dataModel.channel = 'ARD'
            dataModel.id = entry.get('sophoraId')
            dataModel.title = entry.get('broadcastTitle')
            dataModel.aired = entry.get('broadcastDate')[0:19]
            if entry.get('images') and entry.get('images')[0].get('variants'):
                allImages = entry.get('images') and entry.get('images')[0].get('variants')
                #self.logger.debug('allImages {}',allImages)
                for i in allImages:
                    self.logger.debug('allImages element {}',i)
                    if 'gross16x9' in i:
                        dataModel.image = i.get('gross16x9')
                    if 'videowebl' in i:
                        dataModel.image = i.get('videowebl')
            dataModel.url = entry.get('details')
            if dataModel.url.startswith('http:'):
                dataModel.url = dataModel.url.replace('http://','https://')
            #
            resultArray.append(dataModel)
            #
        return resultArray

    def _extractDate(self, rootElement):
        dt = '1970-01-01 00:00:00'
        if rootElement.get('date') is not None and len(rootElement.get('date')) > 0:
          dt = rootElement.get('date')[0:19].replace('T', ' ')
        return dt

    def _extractImage(self, rootElement):
        self.logger.debug('_extractImage from {}',rootElement)
        image = ''
        if rootElement.get('teaserImage') is not None:
            if rootElement.get('teaserImage').get('imageVariants') is not None:
                if rootElement.get('teaserImage').get('imageVariants').get('16x9-512') is not None:
                    image = rootElement.get('teaserImage').get('imageVariants').get('16x9-512')
                elif len(list(rootElement.get('teaserImage').get('imageVariants').keys())) > 0:
                    imageKey = list(rootElement.get('teaserImage').get('imageVariants').keys())[-1]
                    image = rootElement.get('teaserImage').get('imageVariants').get(imageKey)
        self.logger.debug('_extractImage found {}', image)
        return image

    def _extractVideo(self, rootElement):
        self.logger.debug('_extractVideo from {}', rootElement)
        videourl = ''
        if rootElement.get('streams') is not None:
                if rootElement.get('streams').get('adaptivestreaming') is not None:
                    videourl = rootElement.get('streams').get('adaptivestreaming')
                elif len(list(rootElement.get('teaserImage').get('imageVariants').keys())) > 0:
                    videoUrlKey = list(rootElement.get('teaserImage').get('imageVariants').keys())[-1] 
                    videourl = rootElement.get('teaserImage').get('imageVariants').keys().get(videoUrlKey)
        self.logger.debug('_extractVideo found {}', videourl)           
        return videourl
