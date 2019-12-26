# -*- coding=utf8 -*-
#******************************************************************************
# Favorits.py
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
import sqlite3

class Favorits(object):
    "Verwaltet die Favoriten in einer Sqlite-Datenbank."
    
    def __init__(self, dbpath):
        self._conn = self._create_db_connection(dbpath)
    
    def insert(self, actor, url, image):
        "Fügt einen Darsteller in die DB hinzu."
        self.remove(actor)
        c = self._conn.cursor()
        try:
            c.execute("INSERT INTO favorits VALUES(?,?,?)", (actor, url, image))
            self._conn.commit()
        except sqlite3.IntegrityError:
            pass
        
    def remove(self, actor):
        "Entfernt einen Darsteller aus die DB."
        c = self._conn.cursor()
        c.execute("DELETE FROM favorits WHERE actor = ?", (actor,))
        self._conn.commit()
        
    def actor_list(self):
        "Liefert eine Liste mit allen Darstellern, URLs und Images."
        c = self._conn.cursor()
        c.execute("SELECT * FROM favorits")
        result = []
        for (actor, url, image) in c.fetchall():
            result.append(
                ( actor.encode("utf8"),
                  url.encode("utf8"), 
                  image.encode("utf8") 
                )
            )
        return result
        
    def _create_db_connection(self, dbpath):
        "Stellt Verbindung zur DB her - wenn nicht vorhanden wird DB erzeugt." 
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM favorits;")
        except sqlite3.OperationalError:
            c.executescript("CREATE TABLE favorits (actor primary key, url, image);")
        return conn
