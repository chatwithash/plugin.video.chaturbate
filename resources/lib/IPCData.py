# -*- coding=utf8 -*-
#******************************************************************************
# IPCData.py
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
import pickle

class IPCData:
    "DTO für den Datenaustausch zwischen Client/Server"

    def __init__(self, actor, url, seqnr, filename):
        self.actor = actor
        self.url = url
        self.seqnr = seqnr
        self.filename = filename

    @staticmethod
    def dumps(ipcdata_object):
        return pickle.dumps(ipcdata_object)

    @staticmethod
    def loads(dumps_object):
        return pickle.loads(dumps_object)
