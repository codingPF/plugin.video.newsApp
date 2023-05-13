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
import resources.lib.utils as Utils

class DpArd(object):
    """
    DpArd

    """

    def __init__(self):
        self.logger = appContext.LOGGER.getInstance('DpArd')
        self.settings = appContext.SETTINGS
        self.starttime = time.time()


    def loadShows(self):
        #
        resultArray = []
        #
        self.logger.debug('loadShows')
        #
        dataModel = EpisodeModel.EpisodeModel()
        dataModel.channel = 'ARD'
        dataModel.id = 'Y3JpZDovL2Rhc2Vyc3RlLmRlL3RhZ2Vzc2NoYXU'
        dataModel.title = 'Tagesschau'
        dataModel.url = 'https://api.ardmediathek.de/page-gateway/widgets/ard/asset/Y3JpZDovL2Rhc2Vyc3RlLmRlL3RhZ2Vzc2NoYXU?pageNumber=0&pageSize=12'
        dataModel.image = 'https://api.ardmediathek.de/image-service/images/urn:ard:image:c94583f063e6f8c0?w={width}&ch=4c0812e9bf3625ec'
        self.logger.debug('add image for {} {}',dataModel.title, dataModel.image)             
        resultArray.append(dataModel)
        #
        dataModel = EpisodeModel.EpisodeModel()
        dataModel.channel = 'ARD'
        dataModel.id = 'Y3JpZDovL2Rhc2Vyc3RlLmRlL3RhZ2VzdGhlbWVu'
        dataModel.title = 'Tagesthemen'
        dataModel.url = 'https://api.ardmediathek.de/page-gateway/widgets/ard/asset/Y3JpZDovL2Rhc2Vyc3RlLmRlL3RhZ2VzdGhlbWVu?pageNumber=0&pageSize=12'
        dataModel.image = 'https://api.ardmediathek.de/image-service/images/urn:ard:image:a8e169328909960a?w={width}&ch=b5f3166d4dc929aa'
        self.logger.debug('add image for {} {}',dataModel.title,dataModel.image)             
        resultArray.append(dataModel)       
        #
        return resultArray

    def loadTagesschau(self):
        return self.loadEpisodes('https://api.ardmediathek.de/page-gateway/widgets/ard/asset/Y3JpZDovL2Rhc2Vyc3RlLmRlL3RhZ2Vzc2NoYXU?pageNumber=0&pageSize=12')

    def loadEpisodes(self, pUrl):
        #
        resultArray = []
        #
        self.logger.debug('loadEpisodes for {}', pUrl)
        dn = WebResource.WebResource(pUrl)
        dataString = dn.retrieveAsString()
        data = json.loads(dataString)
        data = data.get('teasers')
        for entry in data:
            if self._extractDate(entry).isoformat().count('20:00') > 0:
                self.logger.debug('loadEpisodes episode {}', entry)
                dataModel = EpisodeModel.EpisodeModel()
                dataModel.channel = 'ARD'
                dataModel.id = entry.get('id')
                dataModel.title = entry.get('shortTitle')
                dataModel.aired = self._extractDate(entry).isoformat()
                dataModel.image = Utils.extractJsonValue(entry,'images','aspect16x9','src')
                if dataModel.image:
                    dataModel.image = dataModel.image.format(width = 512)
                dataModel.url = 'https://api.ardmediathek.de/page-gateway/pages/ard/item/{}?embedded=false&mcV6=true'.format(dataModel.id)
                dataModel.mode = 'playArdItem'
                #
                resultArray.append(dataModel)
            #
        return resultArray


    def loadVideoUrl(self, pUrl):
        #
        self.logger.debug('loadVideoUrl for {}', pUrl)
        dn = WebResource.WebResource(pUrl)
        dataString = dn.retrieveAsString()
        data = json.loads(dataString)
        data = Utils.extractJsonValue(data,'widgets',0,'mediaCollection','embedded','streams',0,'media')
        adpativeUrl = None
        mp4Url = None
        for entry in data:
            url = Utils.extractJsonValue(entry,'url')
            if mp4Url is None and url is not None and url.endswith('mp4'):
                mp4Url = url
            if adpativeUrl is None and url is not None and url.endswith('m3u8'):
                adpativeUrl = url
            #
        rt = adpativeUrl or mp4Url
        return rt
    
    
    ######################

    def _extractDate(self, rootElement):
        #
        dt = '1970-01-01T00:00:00Z'
        if rootElement.get('broadcastedOn') is not None and len(rootElement.get('broadcastedOn')) > 0:
          dt = rootElement.get('broadcastedOn')
        #
        self.logger.debug('_extractDate found {}', dt)
        utcTS = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")
        ts = Utils.datetime_from_utc_to_local(utcTS)
        #
        return ts



    def _extractImage(self, rootElement):
        self.logger.debug('_extractImage from {}',rootElement)
        image = ''
        if rootElement.get('teaserImage') is not None:
            if rootElement.get('teaserImage').get('imageVariants') is not None:
                if rootElement.get('teaserImage').get('imageVariants').get('16x9-512') is not None:
                    image = rootElement.get('teaserImage').get('imageVariants').get('16x9-512')
                elif len(list(rootElement.get('teaserImage').get('imageVariants').keys())) > 0:
                    image = list(rootElement.get('teaserImage').get('imageVariants').keys())[-1]
        return image

    def _extractVideo(self, rootElement):
        videourl = ''
        if rootElement.get('streams') is not None:
                if rootElement.get('streams').get('adaptivestreaming') is not None:
                    videourl = rootElement.get('streams').get('adaptivestreaming')
                elif len(list(rootElement.get('teaserImage').get('imageVariants').keys())) > 0:
                    videourl = list(rootElement.get('teaserImage').get('imageVariants').keys())[-1]
        return videourl
