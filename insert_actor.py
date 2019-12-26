#!/usr/bin/env python
#******************************************************************************
# insert_actor.py
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
# -*- coding=utf8 -*-
import sys

from resources.lib.Config import Config
from resources.lib.Favorits import Favorits 

if len(sys.argv) != 2:
    print("USAGE: insert_actor.py actor|url|imageurl")
    exit(1)
else:
    actor, url, image = sys.argv[1].split("|")
    Favorits(Config.FAVORITS_DB).insert(actor, url, image)   
