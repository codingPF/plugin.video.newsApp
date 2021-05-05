'''
Created on 25.01.2021
'''


class EpisodeModel(object):

    def __init__(self):
        self.id = None
        self.title = None
        self.aired = None
        self.url = None
        self.image = None
        self.urlAdaptive = None
        self.duration = None
        self.channel = None

    def init(self, pId, pTitle, pAired, pImage, pUrl, pUrlAdaptive, pDuration, pChannel):
        self.id = pId
        self.title = pTitle
        self.aired = pAired
        self.url = pUrl
        self.image = pImage
        self.urlAdaptive = pUrlAdaptive
        self.duration = pDuration
        self.channel = pChannel
