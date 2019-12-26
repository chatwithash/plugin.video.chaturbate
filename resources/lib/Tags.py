# -*- coding=utf8 -*-
#******************************************************************************
# Tags.py
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
import xbmcaddon

from resources.lib.Scraper import Scraper
from resources.lib.Config import Config

class Tags(Scraper):

    def __init__(self):
        super(Tags, self).__init__()

    def tags_and_rooms(self, category):
        "Liefert eine Liste mit Tag/Raum Tuple."
        return self._sort(self._REGEX_Tags_and_Rooms.findall(self._get_streams_page(category)), category)

    def names_and_images(self, category, tag, page):
        "Liefert eine Liste mit Name/Thumbnail Tuple."
        result = self._REGEX_Name_and_Image.findall(self._get_streams_page_for_actors(category, tag, page))
        if self._Last_Page:
            result.append((None, None))
        return result

    def _sort(self, tags_and_rooms, category):
        "Sortiere Tagliste"
        # alphabetisch
        tags_and_rooms.sort()
        # nach Anzahl Räume
        tags_and_rooms = sorted(tags_and_rooms, key=lambda x: int(x[1]), reverse=True)
        viptags = " %s " % xbmcaddon.Addon(id = Config.PLUGIN_NAME).getSetting(category)
        vip = []
        novip = []
        for tag, rooms in tags_and_rooms:
            space_tag_space = " %s " % tag
            if space_tag_space in viptags:
                vip.append((tag, rooms))
            else:
                novip.append((tag, rooms))
        result = vip
        result.extend(novip)
        return result

    def _get_streams_page(self, category):
        "Liefert die Page als String."
        return self.get_streams_page_in_a_string(self.CATEGORY_URL[category])

    @classmethod
    def mapping(cls, tag):
        "Mappt zwischen Parameter- und URL-Bezeichner."
        mappings = {
            "Tags-Featured": None,
            "Tags-Weiblich": "female",
            "Tags-Maennlich": "male",
            "Tags-Paar": "couple",
            "Tags-Transsexual": "transsexual"
        }
        return mappings[tag]
