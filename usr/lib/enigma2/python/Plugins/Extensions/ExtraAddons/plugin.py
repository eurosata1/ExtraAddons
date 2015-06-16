# Embedded file name: /usr/lib/enigma2/python/Plugins/Extensions/ExtraAddons/plugin.py
from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
import xml.dom.minidom
import os
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from twisted.web.client import downloadPage
import urllib
from Components.Label import Label

class Getipklist(Screen):
    skin = '\n\t\t<screen position="center,center" size="955,400" title="ExtraAddons" >\n\t\t\t\n                                       <widget name="list" position="50,20" size="500,300" scrollbarMode="showOnDemand" />\n\n\t\t\t\n\t\t\t<eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" />\n\t\t\t<widget name="info" position="150,50" zPosition="4" size="300,300" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n\t                  <ePixmap position="5,365" zPosition="4" size="530,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtraAddons/about.png" transparent="1" alphatest="on" />\n\t\n\t    <ePixmap position="580,center" zPosition="2" size="400,400" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtraAddons/eurosatlogo.png" transparent="1" alphatest="on" />\n\t\n\t\t</screen>'

    def __init__(self, session):
        self.skin = Getipklist.skin
        Screen.__init__(self, session)
        self.list = []
        self['list'] = MenuList([])
        self['info'] = Label()
        self.addon = 'emu'
        self.icount = 0
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        self['info'].setText('Downloading list...')
        xurl = 'http://www.euro-sat-image.com/paneladdons.xml'
        print 'xurl =', xurl
        xdest = '/usr/lib/enigma2/python/Plugins/Extensions/ExtraAddons/paneladdons.xml'
        print 'xdest =', xdest
        try:
            xlist = urllib.urlretrieve(xurl, xdest)
            myfile = file('/usr/lib/enigma2/python/Plugins/Extensions/ExtraAddons/paneladdons.xml')
            self.data = []
            self.names = []
            icount = 0
            list = []
            xmlparse = xml.dom.minidom.parse(myfile)
            self.xmlparse = xmlparse
            for plugins in xmlparse.getElementsByTagName('plugins'):
                self.names.append(plugins.getAttribute('cont').encode('utf8'))

            self['actions'] = ActionMap(['OkCancelActions'], {'ok': self.okClicked,
             'cancel': self.close}, -1)
            self.list = list
            self['info'].setText('')
            self['list'].setList(self.names)
            self.downloading = True
        except:
            self['actions'] = ActionMap(['OkCancelActions'], {'ok': self.close,
             'cancel': self.close}, -1)
            self.downloading = False
            self['info'].setText('ExtraAddons in maintenance ... please try again later')

    def setWindowTitle(self):
        self.setTitle(_('Dowanloding'))

    def okClicked(self):
        selection = str(self['list'].getCurrent())
        self.session.open(SelectCountry, self.xmlparse, selection)


class SelectCountry(Screen):
    skin = '\n\t\t<screen position="center,center" size="950,430" title="ExtraAddons" >\n\t\t\t  <widget name="countrymenu" position="10,0" size="500,380" scrollbarMode="showOnDemand" />\n\t                  <ePixmap position="5,395" zPosition="4" size="590,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtraAddons/about.png" transparent="1" alphatest="on" />\n\t           <ePixmap position="580,center" zPosition="2" size="400,400" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtraAddons/eurosatlogo.png" transparent="1" alphatest="on" />\n\t</screen>\n\t\t'

    def __init__(self, session, xmlparse, selection):
        self.skin = SelectCountry.skin
        Screen.__init__(self, session)
        self.xmlparse = xmlparse
        self.selection = selection
        list = []
        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    list.append(plugin.getAttribute('name').encode('utf8'))

        self['countrymenu'] = MenuList(list)
        self['actions'] = ActionMap(['SetupActions'], {'ok': self.selCountry,
         'cancel': self.close}, -2)

    def downloadError(self, raw):
        print '[e2Fetcher.fetchPage]: download Error', raw
        self.session.open(MessageBox, text=_('Error downloading: ') + self.path, type=MessageBox.TYPE_ERROR)

    def downloadDone(self, raw):
        print '[e2Fetcher.fetchPage]: download done', raw
        self.session.open(PictureScreen, picPath=self.path)

    def selCountry(self):
        selection_country = self['countrymenu'].getCurrent()
        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.prombt(urlserver, pluginname)

    def prombt(self, com, dom):
        self.session.open(Console, _('downloading-installing: %s') % dom, ['ipkg install -force-overwrite %s' % com])


def main(session, **kwargs):
    session.open(Getipklist)


def Plugins(**kwargs):
    return PluginDescriptor(name='Extra Addons', description=_('Download your favorite plugin from EuroSat'), where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], icon='addons.png', fnc=main)
