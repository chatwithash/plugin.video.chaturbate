# -*- coding=utf8 -*-
#******************************************************************************
# Actors.py
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

from resources.lib.Config import Config
from resources.lib.Scraper import Scraper
from resources.lib.Tags import Tags
import xbmc


class Actors(Scraper):

    def __init__(self):
        super(Actors, self).__init__()

    def names_and_images(self, category, page, tag=None):
        "Liefert eine Liste mit Name/Thumbnail Tuple."
        result = self._REGEX_Name_and_Image.findall(self._get_streams_page(category, page, tag))
        if self._Last_Page:
            result.append((None, None))
        return result

    def _get_streams_page(self, category, page, tag=None):
        "Liefert die Homepage in einem String."
        if tag:
            tagmap = Tags.mapping(category)
            if tagmap:
                url = "%stag/%s/%s?page=%d" % (Config.CHATURBATE_URL, tag, tagmap, int(page))
            else:
                url = "%stag/%s?page=%d" % (Config.CHATURBATE_URL, tag, int(page))
        else:
            url = self.CATEGORY_URL[category] + "?page=%d" % (int(page))
        return self.get_streams_page_in_a_string(url)

