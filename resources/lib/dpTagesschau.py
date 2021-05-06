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
