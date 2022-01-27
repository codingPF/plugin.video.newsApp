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
        dn = WebResource.WebResource('https://www.tagesschau.de/api2/channels')
        dataString = dn.retrieveAsString()
        data = json.loads(dataString)
        #
        data = data.get('channels')
        for channel in data:
            dataModel = EpisodeModel.EpisodeModel()
            dataModel.channel = 'ARD'
            dataModel.id = channel.get('sophoraId')
            dataModel.title = channel.get('title')
            if channel.get('date') is not None:
                if len(channel.get('date')) > 0:
                    dataModel.aired = channel.get('date')[0:19].replace('T', ' ')
            #
            if channel.get('teaserImage') is not None:
                if channel.get('teaserImage').get('videowebl') is not None:
                    dataModel.image = channel.get('teaserImage').get('videowebl').get('imageurl')
                elif channel.get('teaserImage').get('portraetgrossplus8x9') is not None:
                    dataModel.image = channel.get('teaserImage').get('portraetgrossplus8x9').get('imageurl')
                elif channel.get('teaserImage').get('videowebm') is not None:
                    dataModel.image = channel.get('teaserImage').get('videowebm').get('imageurl')
            #
            if channel.get('streams') is not None:
                if channel.get('streams').get('adaptivestreaming') is not None:
                    dataModel.urlAdaptive = channel.get('streams').get('adaptivestreaming')
                if channel.get('streams').get('h264xl') is not None:
                    dataModel.url = channel.get('streams').get('h264xl')
                elif channel.get('streams').get('h264m') is not None:
                    dataModel.url = channel.get('streams').get('h264m')
                elif channel.get('streams').get('h264s') is not None:
                    dataModel.url = channel.get('streams').get('h264s')
            #
            startTime = channel.get('start')
            endTime = channel.get('end')
            if dataModel.title.startswith('Aktuelle Sendung') and startTime is not None and endTime is not None:
                startTime = startTime.replace('.000+', '+')
                endTime = endTime.replace('.000+', '+')
                dataModel.urlAdaptive = dataModel.urlAdaptive + '?start={}&end={}'.format(startTime, endTime)
                dataModel.aired = startTime[0:19].replace('T', ' ')
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
        showIndexPage = {}
        showImage = {}
        #
        dn = WebResource.WebResource('http://www.tagesschau.de/api/multimedia/sendung/letztesendungen100~_week-true.json')
        dataString = dn.retrieveAsString()
        # load all top show urls to have the index page for all episodes
        data = json.loads(dataString)
        for topUrls in data.get('broadcastsPerTypeUrls'):
            showIndexPage[topUrls.get('broadcastTitle')]=topUrls.get('url')
            #self.logger.debug('show index {} {}',topUrls.get('broadcastTitle'),topUrls.get('url'))
        # lets go into the shows to get the image and make sure we only take shows with episodes
        for entry in data.get('latestBroadcastsPerType'):
            
            if entry.get('broadcastTitle') not in showImage:
                img = ''
                if entry.get('images') and entry.get('images')[0].get('variants'):
                        allImages = entry.get('images') and entry.get('images')[0].get('variants')
                        #self.logger.debug('allImages {}',allImages)
                        for i in allImages:
                            #self.logger.debug('allImages element {}',i)
                            if 'gross16x9' in i:
                                img = i.get('gross16x9')
                            if 'videowebl' in i:
                                img = i.get('videowebl')
                showImage[entry.get('broadcastTitle')]=img
                self.logger.debug('add image for {} {}',entry.get('broadcastTitle'),img)             
        # merge the data from image to index because the index contains old shows
        for k,v in showImage.items():
            dataModel = EpisodeModel.EpisodeModel()
            dataModel.channel = 'ARD'
            dataModel.id = k
            dataModel.title = k
            dataModel.url = showIndexPage[k]
            dataModel.image = v
            #self.logger.debug('create show for {} {} {}',k,v,showIndexPage[k])
            resultArray.append(dataModel)
        
        
            #
        return resultArray

    def loadBroadcasts(self, pUrl):
        #
        resultArray = []
        #
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
                self.logger.debug('allImages {}',allImages)
                for i in allImages:
                    self.logger.debug('allImages element {}',i)
                    if 'gross16x9' in i:
                        dataModel.image = i.get('gross16x9')
                    if 'videowebl' in i:
                        dataModel.image = i.get('videowebl')
            dataModel.url = entry.get('details')
            #
            resultArray.append(dataModel)
            #
        return resultArray

        