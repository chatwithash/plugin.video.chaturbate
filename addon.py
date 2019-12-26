# -*- coding=utf8 -*-
#******************************************************************************
# addon.py
#------------------------------------------------------------------------------
#
# Copyright (c) 2014-2017 LivingOn <LivingOn@xmail.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#******************************************************************************
import os
import sys
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import urllib

from resources.lib.Config import Config
from resources.lib.ChunkPlayer import ChunkPlayer
from resources.lib.Texture13DB import Texture13DB
from resources.lib.Actors import Actors
from resources.lib.Tags import Tags
from resources.lib.Favorits import Favorits
from resources.lib.OnlineStatus import OnlineStatus

class Chaturbate(object):
    "XBMC-AddOn zum Zugriff auf die Hauptseite von www.chaturbate.com."
     
    _plugin_id      = None
    _addon          = None
    _streams        = None
    
    def __init__(self):
        "Initialisiere AddOn."
        self._register_addon()
        self._process_request()
        
    def _register_addon(self):
        "Registriere AddOn."
        self._plugin_id = int(sys.argv[1])
        self._addon = xbmcaddon.Addon(id = Config.PLUGIN_NAME)
        self._create_settings_file()

    def _process_request(self):
        "Ermittel die Benutzeranfrage und führe sie aus."
        if sys.argv[2]:
            urlparam = sys.argv[2]
            if "actor=" in urlparam:
                self._play_stream(urlparam)
            elif "tag=" in urlparam:
                self._create_tagmenue_actors(urlparam)
            elif "category=" in urlparam:
                self._create_submenue_actors(urlparam)
            elif "submenue=Kategorien" in urlparam:
                self._create_submenue_category()
            elif "submenue=Schlagworte" in urlparam:
                self._create_submenue_tags()
            elif "submenue=Favoriten" in urlparam:
                self._create_submenue_favorits()
            elif "submenue=Aufzeichnungen" in urlparam:
                self._start_filemanager()
            elif "submenue=Tags-" in urlparam:
                self._create_tagmenue(urlparam)
        else:
            self._create_submenues()
 
    def _create_submenues(self):
        submenues = (
            (30110, "Kategorien"),
            (30112, "Schlagworte"),
            (30115, "Favoriten"), 
            (30120, "Aufzeichnungen")
        )
        items = []
        for (i18n, submenue) in submenues:
            url = sys.argv[0] + "?" + urllib.urlencode({
                'submenue': submenue,
            })
            item = xbmcgui.ListItem(self._addon.getLocalizedString(i18n))
            item.addContextMenuItems(
                self._create_context_submenues()
            )
            items.append((url, item, True))
        xbmcplugin.addDirectoryItems(self._plugin_id, items)
        xbmcplugin.endOfDirectory(self._plugin_id)

    def _create_submenue_category(self):
        categories = (
            (30130, "Featured"), 
            (30135, "Weiblich"),
            (30140, "Maennlich"),
            (30145, "Paar"),
            (30150, "Transsexual")
        )
        items = []
        for (i18n, category) in categories:
            url = sys.argv[0] + "?" + urllib.urlencode({
                'category': category,
                'page': 1
            })
            item = xbmcgui.ListItem(self._addon.getLocalizedString(i18n))
            item.addContextMenuItems(
                self._create_context_submenues()
            )
            items.append((url, item, True))
        xbmcplugin.addDirectoryItems(self._plugin_id, items)
        xbmcplugin.endOfDirectory(self._plugin_id)
 
    def _create_submenue_actors(self, urlparam):
        Texture13DB.clean_database()
        category, page = urlparam.split("&")
        category = category.split("=")[1]
        page = page.split("=")[1]
        self._create_actor_list(category, page)

    def _create_submenue_tags(self):
        categories = (
            (30130, "Tags-Featured"),
            (30135, "Tags-Weiblich"),
            (30140, "Tags-Maennlich"),
            (30145, "Tags-Paar"),
            (30150, "Tags-Transsexual")
        )
        items = []
        for (i18n, category) in categories:
            url = sys.argv[0] + "?" + urllib.urlencode({
                'submenue': category,
                'page' : 1
            })
            item = xbmcgui.ListItem(self._addon.getLocalizedString(i18n))
            item.addContextMenuItems(
                self._create_context_submenues()
            )
            items.append((url, item, True))
        xbmcplugin.addDirectoryItems(self._plugin_id, items)
        xbmcplugin.endOfDirectory(self._plugin_id)

    def _create_tagmenue(self, urlparam):
        param = {}
        for name_value in urlparam[1:].split("&"):
            name, value = name_value.split("=")
            param[name] = value
        items = []
        for (tag, rooms) in Tags().tags_and_rooms(param["submenue"]):
            tagroom = "%s (%s)" % (tag, rooms)
            url = sys.argv[0] + "?submenue=%s&tag=%s" % (param["submenue"], tag)
            item = xbmcgui.ListItem(tagroom)
            item.addContextMenuItems(
                self._create_context_submenues()
            )
            items.append((url, item, True))
        xbmcplugin.addDirectoryItems(self._plugin_id, items)
        xbmcplugin.endOfDirectory(self._plugin_id)
        xbmc.executebuiltin("Container.SetViewMode(502)")

    def _create_tagmenue_actors(self, urlparam):
        Texture13DB.clean_database()
        param = {}
        for name_value in urlparam[1:].split("&"):
            name, value = name_value.split("=")
            param[name] = value
        page = (param["page"] if "page" in param else 1)
        self._create_actor_list(param["submenue"], page, param["tag"])

    def _create_submenue_favorits(self):
        items = []
        Texture13DB.clean_database()
        actor_list = Favorits(Config.FAVORITS_DB).actor_list()
        actor_list.sort()
        status = OnlineStatus()
        only_active_favorits = self._addon.getSetting("only_active_favorits")
        # Da sich die Thumbnail-URL mit der Zeit ändern kann, wird nicht die DB-Version
        # verwendet sondern immer "frisch" ermittelt.
        for (actor, url, image) in actor_list:
            if only_active_favorits == "true" and not status.is_online(image):
                continue
            item = xbmcgui.ListItem(actor, iconImage=image)
            item.addContextMenuItems(
                self._create_context_menu_favorits(actor)
            )
            item_info = {}
            item_info['cast'] = ([actor])
            item_info['genre'] = 'Porn'
            item_info['studio'] = 'Chaturbate'
            item.setInfo(type='video', infoLabels=item_info)
            item.setArt({'poster': image})
            items.append((url, item, True))
        xbmcplugin.addDirectoryItems(self._plugin_id, items)
        xbmcplugin.endOfDirectory(self._plugin_id, cacheToDisc=True)
        xbmc.executebuiltin("Container.SetViewMode(500)")
        
    def _start_filemanager(self):
        folder = self._addon.getSetting("record_folder")
        xbmc.executebuiltin('ActivateWindow(Filemanager,%s)' % folder) 
 
    def _create_actor_list(self, category, page, tag=None):
        last_page = False
        items = []
        for name, image in Actors().names_and_images(category, page, tag):
            if name and image:
                url = sys.argv[0] + "?" + urllib.urlencode({'actor' : name})
                item = xbmcgui.ListItem(name, iconImage=image)
                item.addContextMenuItems(
                    self._create_context_menu_for_actor(name, url, image)
                )
                items.append((url, item, True,))
            else:
                last_page = True
        param = {'page': int(page) + 1}
        if tag:
            param["submenue"] = category
            param["tag"] = tag
        else:
            param["category"] = category
        url = sys.argv[0] + "?" + urllib.urlencode(param)
        if not last_page:
            items.append((url, 
                xbmcgui.ListItem(
                    self._addon.getLocalizedString(30160), 
                    iconImage='DefaultFolder.png') , True
                )
            )            
        xbmcplugin.addDirectoryItems(self._plugin_id, items)
        xbmcplugin.endOfDirectory(self._plugin_id, cacheToDisc=True)
        xbmc.executebuiltin("Container.SetViewMode(500)")

    def _create_context_submenues(self):
        command = []
        command.append((self._addon.getLocalizedString(30169), self._cmd_settings(),))
        return command

    def _create_context_menu_for_actor(self, name, url, image):
        command = []
        command.append((self._addon.getLocalizedString(30169), self._cmd_settings(),))
        command.append(('Refresh', 'Container.Refresh',))
        command.append((self._addon.getLocalizedString(30170), self._cmd_insert_favorite(name, url, image),))
        return command

    def _create_context_menu_favorits(self, name):
        command = []
        command.append((self._addon.getLocalizedString(30169), self._cmd_settings(),))
        command.append(('Refresh', 'Container.Refresh',))
        command.append((self._addon.getLocalizedString(30175), self._cmd_remove_favorite(name),))
        return command

    def _cmd_settings(self):
        return "XBMC.RunScript(%s)" % (
            "%s/%s" % (self._get_base_dir(), Config.SCRIPT_SETTINGS)
        )

    def _cmd_insert_favorite(self, name, url, image):
        return "XBMC.RunScript(%s, %s)" % (
            "%s/%s" % (self._get_base_dir(), Config.SCRIPT_INSERT_FAVORITE),
            "%s|%s|%s" % (name, url, image)
        )

    def _cmd_remove_favorite(self, name):
        return "XBMC.RunScript(%s, %s)" % (
            "%s/%s" % (self._get_base_dir(), Config.SCRIPT_REMOVE_FAVORITE),
            name
        )

    def _play_stream(self, urlparam):
        "Spiele den Stream mit dem ChunkPlayer ab."
        actor = urlparam.split("=")[1]
        faststream = True if self._addon.getSetting("FastStream") == 'true' else False
        cp = ChunkPlayer(self._plugin_id, faststream)
        cp.play_stream(actor)

    def _create_settings_file(self):
        self._addon.setSetting("","")

    def _get_base_dir(self):
        return os.path.dirname(__file__) 
            
if __name__ == "__main__":
    Chaturbate()
                
