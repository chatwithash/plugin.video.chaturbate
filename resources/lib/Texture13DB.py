# -*- coding=utf8 -*-
#******************************************************************************
# Texture13DB.py
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
import xbmc
import sqlite3

from resources.lib.Config import Config


class Texture13DB(object):
    "Sorgt für aktuelle Thumbnails in der Darstellung."
    
    @classmethod
    def clean_database(cls):
        "Löscht die Texture13.db und den lokalen Cache."
        conn = sqlite3.connect(xbmc.translatePath("special://database/Textures13.db"))
        try:
            with conn:
                conn.execute("DELETE FROM texture WHERE url LIKE '%roomimg%';")
        except:
            pass
