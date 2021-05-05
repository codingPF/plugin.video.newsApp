# -*- coding: utf-8 -*-
"""
Kodi Interface

SPDX-License-Identifier: MIT
"""
import datetime

import resources.lib.appContext as appContext
import xbmcgui
import xbmcplugin
import resources.lib.utils as pyUtils


class EpisodeUI(object):

    def __init__(self, pAddon):
        self.logger = appContext.LOGGER.getInstance('EpisodeUI')
        self.setting = appContext.SETTINGS
        self.addon = pAddon
        self.tzBase = datetime.datetime.fromtimestamp(0)
        self.allSortMethods = [
            xbmcplugin.SORT_METHOD_TITLE,
            xbmcplugin.SORT_METHOD_DATE,
            xbmcplugin.SORT_METHOD_DATEADDED
        ]

        self.id = 0
        self.title = ''
        self.aired = ''
        self.url = ''
        self.image = ''
        self.urlAdaptive = ''
        self.duration = 0

    def generate(self, pData):
        #
        xbmcplugin.addSortMethod(self.addon.addon_handle, xbmcplugin.SORT_METHOD_DATEADDED)
        xbmcplugin.setContent(self.addon.addon_handle, 'video')
        #
        listOfElements = []
        for episodeModel in pData:
            #
            self.logger.debug('{} - {} - {} - {} - {} - {} - {}', episodeModel.id, episodeModel.title, episodeModel.aired, episodeModel.duration, episodeModel.image, episodeModel.url, episodeModel.urlAdaptive)
            #
            (targetUrl, listItem, isFolder) = self._generateListItem(episodeModel)
            #
            listItem.addContextMenuItems(self._generateContextMenu(episodeModel))
            #
            listOfElements.append((targetUrl, listItem, isFolder))
        #
        xbmcplugin.addDirectoryItems(
            handle=self.addon.addon_handle,
            items=listOfElements,
            totalItems=len(listOfElements)
        )
        #
        xbmcplugin.endOfDirectory(self.addon.addon_handle, cacheToDisc=True)
        # self.addon.setViewId(self.addon.resolveViewId('THUMBNAIL'))

    def _generateListItem(self, pEpisode):
        #
        tgtUrl = self.addon.generateUrl({
                    'mode': "play",
                    'channel': pEpisode.channel,
                    'urlB64': pyUtils.b64encode(pEpisode.urlAdaptive)
                })
        #
        info_labels = {
            'title': pEpisode.title,
            'sorttitle': pEpisode.title.lower(),
            'tvshowtitle': pEpisode.title,
            'plot': pEpisode.title
        }

        if pEpisode.aired is not None:
            airedstring = pEpisode.aired.replace('T', ' ')
            info_labels['date'] = airedstring[:10]
            info_labels['aired'] = airedstring[:10]
            info_labels['dateadded'] = airedstring
            info_labels['plot'] = self.addon.localizeString(30101).format(airedstring) + info_labels['plot']
        #
        if pEpisode.duration is not None:
            info_labels['duration'] = '{:02d}:{:02d}:00'.format(*divmod(pEpisode.duration, 60))

        icon = pEpisode.image

        #
        if self.addon.getKodiVersion() > 17:
            listitem = xbmcgui.ListItem(label=pEpisode.title, path=tgtUrl, offscreen=True)
        else:
            listitem = xbmcgui.ListItem(label=pEpisode.title, path=tgtUrl)
        #
        listitem.setInfo(type='video', infoLabels=info_labels)
        listitem.setProperty('IsPlayable', 'true')
        listitem.setArt({
            'thumb': icon,
            'icon': icon,
            'fanart': icon
        })
        #
        self.logger.debug("URL {} icon {}", pEpisode.url, icon)
        #
        return (tgtUrl, listitem, False)

    def _generateContextMenu(self, pEpisode):
        contextmenu = []
        """
        contextmenu.append((
            self.addon.localizeString(30100),
            'RunPlugin({})'.format(
                self.addon.generateUrl({
                    'mode': "download",
                    'id': pEpisode.id
                })
            )
        ))
        """
        return contextmenu

