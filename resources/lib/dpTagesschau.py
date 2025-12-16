# -*- coding: utf-8 -*-
"""
Data provider for Tagesschau

SPDX-License-Identifier: MIT
"""

# pylint: disable=too-many-lines,line-too-long
import json
import time
import datetime
from ckfw.webResource import WebResource
from ckfw.params import Params


class DpTagesschau(object):
    """
    DpTagesschau

    """

    def __init__(self, pAddon):
        self.addon = pAddon
        self.logger = self.addon.createLogger('DpTagesschau')
        self.starttime = time.time()

    def loadData(self):
        #
        resultArray = []
        #
        self.logger.debug('loadData')
        dn = WebResource(self.addon, 'https://www.tagesschau.de/api2u/channels')
        dataString = dn.retrieveAsString()
        data = json.loads(dataString)
        #
        data = data.get('channels')
        for channel in data:
            dataModel = Params()
            dataModel.channel = 'ARD'
            dataModel.id = channel.get('sophoraId')
            dataModel.title = channel.get('title')
            dataModel.aired = self._extractDate(channel)
            dataModel.image = self._extractImage(channel)
            dataModel.url = self._extractVideo(channel)
            dataModel.duration = self._extractDuration(channel)
            dataModel.urlAdaptive = dataModel.url
            dataModel.mode = 'play'
            #
            # sometimes title is empty
            if dataModel.title is None:
                dataModel.title = self._extractTrackingTitle(channel)
            #
            startTime = channel.get('start')
            endTime = channel.get('end')
            if dataModel.title is not None and dataModel.title.startswith('Aktuelle Sendung: Tagesthemen') and startTime is not None and endTime is not None:
                dataModel.urlAdaptive = dataModel.urlAdaptive + '?start={}&end={}'.format(startTime, (startTime+1000)) #??
                self.logger.debug('Aktuelle Sendung {}',dataModel.urlAdaptive)
                self.logger.debug('Aktuelle Sendung Times start {} end {}',startTime,endTime)
                dataModel.aired = datetime.datetime.fromtimestamp(startTime).isoformat()
            elif dataModel.title is not None and dataModel.title.startswith('Aktuelle Sendung') and startTime is not None and endTime is not None:
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
        dn = WebResource(self.addon, pUrl)
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
        dn = WebResource(self.addon, 'https://www.tagesschau.de/api2u/news')
        dataString = dn.retrieveAsString()
        # load all top show urls to have the index page for all episodes
        data = json.loads(dataString)
        for entry in data.get('news'):            
            if entry.get('type') == 'video':
                dataModel = Params()
                dataModel.channel = 'ARD'
                dataModel.id = entry.get('sophoraId')
                dataModel.title = entry.get('title')
                dataModel.aired = self._extractDate(entry)
                dataModel.url = self._extractVideo(entry)
                dataModel.image = self._extractImage(entry)
                dataModel.duration = self._extractDuration(entry);
                self.logger.debug('add image for {} {}',dataModel.title,dataModel.image)             
                resultArray.append(dataModel)
            #
        return resultArray

    def loadBroadcasts(self, pUrl):
        #
        resultArray = []
        #
        self.logger.debug('loadBroadcasts')
        dn = WebResource(self.addon, pUrl)
        dataString = dn.retrieveAsString()
        data = json.loads(dataString)
        data = data.get('latestBroadcastsPerType')
        for entry in data:
            dataModel = Params()
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

    def loadArchive(self, pDate):
        #
        resultArray = []
        #
        self.logger.debug('loadArchive ' + pDate)
        dn = WebResource(self.addon, 'https://www.tagesschau.de/archiv/sendungen?datum='+pDate)
        dataString = dn.retrieveAsString()
        dataString = dataString.decode("utf-8")        
        import re
        import html
        import datetime as dt
        pattern = re.compile(
            r'data-v\s*=\s*"(.+?)"\s+data-v-type',
            re.DOTALL
        )
        matches = pattern.findall(dataString)
        parsed = []
        for raw in matches:
            decoded = html.unescape(raw)
            try:
                jsonObject = json.loads(decoded)
                if jsonObject.get('mc'):
                    parsed.append(jsonObject)
            except json.JSONDecodeError:
                pass  # ungültige JSONs ignorieren
        for entry in parsed:
            dataModel = Params()
            dataModel.channel = 'ARD'
            dataModel.id = entry.get('mc').get('meta').get('title')
            dataModel.title = entry.get('mc').get('meta').get('title')
            ts = entry.get('mc').get('meta').get('broadcastedOnDateTime')
            if ts:
                ts = ts[:-2] + ":" + ts[-2:]
                dt_utc = datetime.datetime.fromisoformat(ts)
                dt_local = dt_utc.astimezone()
                #dt_utc = dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S%z")
                #dt_local = dt_utc.astimezone()
                local_iso = dt_local.isoformat()
                dataModel.aired = local_iso[0:19]
            dataModel.url = entry.get('mc').get('streams')[0].get('media')[-1].get('url')
            dataModel.image = entry.get('mc').get('meta').get('images')[0].get('url').replace('{size}','1x1-small').replace('{width}','512');
            dataModel.duration = int(entry.get('mc').get('pluginData').get('trackingAgf@all').get('clipData').get('length'))
            self.logger.debug('entry {}', dataModel)             
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
                    videourl = rootElement.get('teaserImage').get('imageVariants').get(videoUrlKey)
        self.logger.debug('_extractVideo found {}', videourl)           
        return videourl

    def _extractTrackingTitle(self, rootElement):
        self.logger.debug('_extractTrackingTitle from {}', rootElement)
        altTitle = 'UNK'
        if rootElement.get('tracking') is not None:
            if len(rootElement.get('tracking')) > 1:
                if rootElement.get('tracking')[1].get('title') is not None:
                    altTitle = rootElement.get('tracking')[1].get('title')
                    self.logger.debug('_extractTrackingTitle found {}', altTitle)           
        return altTitle

    def _extractDuration(self, rootElement):
        self.logger.debug('_extractDuration from {}', rootElement)
        duration = 0;
        if rootElement.get('tracking') is not None:
            if len(rootElement.get('tracking')) > 1:
                if rootElement.get('tracking')[1].get('length') is not None:
                    duration = int(rootElement.get('tracking')[1].get('length'))
                    self.logger.debug('_extractDuration found {}', duration)           
        return duration