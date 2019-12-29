# -*- coding=utf8 -*-
#******************************************************************************
# ChunkPlayer.py
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
import re
import time
import socket
import urllib2
import json
import xbmc
import xbmcgui
import xbmcaddon

from resources.lib.Config import Config
from resources.lib.IPCData import IPCData

class ChunkPlayer(object):
    "Sammelt die Chunks ein und spielt sie ab."

    def __init__(self, plugin_id, faststream=True):
        self._plugin_id = plugin_id
        self._faststream = faststream
        self._addon = xbmcaddon.Addon()
     
    def play_stream(self, actor):
        if self._addon.getSetting("record_active") == "false":
            self._direct_play(actor)
        else:
            if self._check_for_recording_service():
                self._record_play(actor)
            else:
                self._direct_play(actor)

    def _direct_play(self, actor):
        thumb = Config.THUMBURL + actor + ".jpg"
        listitem = xbmcgui.ListItem(actor)
        listitem.setArt({'poster': thumb, 'thumb': thumb})
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        room_data = {}
        try:
            room_data = _PlaylistAnylyser(self._faststream).get_playlist(actor)
            listitem.setInfo('video', room_data)
            listitem.setProperty('IsPlayable', 'true')
            play_url = room_data['path'] + '|Origin=https://chaturbate.com&Referer=https://chaturbate.com/&User-Agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
            playlist.add(play_url, listitem)
            xbmc.Player().play(playlist)
        except:
            xbmc.log("Failed to find playlist({})".format(room_data),level=xbmc.LOGNOTICE)

    def _record_play(self, actor):
        pa = _PlaylistAnylyser(self._faststream)
        streamurl, sequencenr =  pa.get_streamurl_and_sequencenr(actor)
        if streamurl and sequencenr:
            self._start_recording(actor, streamurl, sequencenr)
        else:
            addon = xbmcaddon.Addon(id = Config.PLUGIN_NAME)
            title = addon.getLocalizedString(30180)
            msg = addon.getLocalizedString(30185) % actor
            xbmcgui.Dialog().ok(title, msg)

    def _start_recording(self, actor, url, seqnr):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', Config.CHUNK_PLAYER_PORT)
        sock.connect(server_address)
        try:
            filename = self._get_filename(actor)
            ipc1 = IPCData(actor, url, seqnr, filename)
            data = IPCData.dumps(ipc1)
            sock.sendall(data)
        finally:
            sock.close()

    def _get_filename(self, actor):
        filename = ''
        active = True if self._addon.getSetting("record_active") == "true" else False
        if active:
            recordtype = self._addon.getSetting("record_type")
            folder = self._addon.getSetting("record_folder").rstrip(os.sep)
            timestamp = time.strftime('%Y-%m-%d__%H.%M.%S')
            filename = "%s%s%s_%s.mp4" % (folder, os.sep, actor, timestamp)
            # bei einmaliger Aufnahme den Rekorder wieder deaktivieren
            if recordtype == "0":
                self._addon.setSetting("record_active", "false")
        return filename

    def _check_for_recording_service(self):
        if self._addon.getSetting("record_active") == "true":
            service_exists = xbmc.getCondVisibility("System.HasAddon(service.chaturbate_recorder)")
            if not service_exists:
                title = self._addon.getLocalizedString(30700)
                msg = self._addon.getLocalizedString(30710)
                xbmcgui.Dialog().ok(title, msg)
                self._addon.setSetting("record_active", "false")
                return False
        return True


class _PlaylistAnylyser(object):
    "Ermittelt die URL und Sequenznummer der einzelnen Chunks."

    def __init__(self, faststream):
        self._faststream = faststream

    def get_streamurl_and_sequencenr(self, actor):
        "Liefert die Stream-URL und die Sequenznummer."
        playlist = self.get_playlist(actor)
        if playlist:
            streambase = self._get_playlist_url(playlist)
            chunkurl = self._get_chunk_url(streambase, playlist)
            if chunkurl:
                chunkcontent = self._get_chunk_content(chunkurl)
                sequencenr = self._get_sequence_nr(chunkcontent)
                mediabase = self._get_mediabase(streambase, chunkcontent)
                return (mediabase, sequencenr)
            else:
                return (None, None)
        else:
            return (None, None)

    def _get_metadata(self, actor, data):
        "Build metadata"
        room_json, room_data, plot_data = {}, {}, {}
        try:
            room_json = json.loads(data)
            room_data['cast'] = ([actor])
            room_data['studio'] = (["Chaturbate"])
            room_data['mediatype'] = "video"
            room_data['mpaa'] = "XXX"
            room_data['genre'] = "Porn"
            room_data['status'] = room_json["room_status"]
            room_data['path'] = room_json["hls_source"]
            room_data['title'] = room_json["room_title"]
            plot_data['viewers'] = room_json["num_viewers"]
            plot_data['gender'] = room_json["broadcaster_gender"]
            room_data['plot'] = "[B]Model:[/B] [COLOR deeppink]{}[/COLOR][CR]".format(actor)
            room_data['plot'] += "[B]Gender:[/B] [COLOR deeppink]{}[/COLOR][CR]".format(plot_data['gender'])
            room_data['plot'] += "[B]Viewers:[/B] [COLOR deeppink]{}[/COLOR][CR]".format(plot_data['viewers'])
            room_data['plot'] += "[B]Genre:[/B] [COLOR deeppink]{}[/COLOR]".format(room_data['genre'])
        except Exception as inst:
            xbmc.log("Chaturbate: {} : {} ".format(inst,room_data), level=xbmc.LOGNOTICE)

        return (room_data)
        
    def get_playlist(self, actor):
        "Liefert die *.m3u8-Playlist."
        url = "%s/%s" % (Config.CHATURBATE_API, actor)
        request = urllib2.Request(url)
        request.add_header('User-Agent', Config.USER_AGENT)
        data = urllib2.urlopen(request).read()
        room_data = {}
        public_status = "public"

        try:
            room_data = self._get_metadata(actor, data)
        except Exception as inst:
            xbmc.log("Chaturbate: {} ".format(inst), level=xbmc.LOGNOTICE)

        if public_status not in room_data['status']:
            xbmc.executebuiltin("Notification(%s, %s %s)"%(actor, "is currently ", room_data['status'])) 
        else:
            #we need to stop the player, before playing next stream
            #otherwise setInfo fails
            xbmc.Player().stop()
            return room_data

    def _get_playlist_url(self, playlist):
        "Liefert die URL der Playlist."
        return re.findall(r'(.*)playlist.*', playlist)[0]

    def _get_chunk_url(self, streambase, playlist):
        "Liefert die URL zur Chunk-Playlist."
        try:
            data = urllib2.urlopen(playlist).read()
            stream = re.findall(r'(chunk.*)', data)[0]
            return "%s%s" % (streambase, stream)
        except:
            return None

    def _get_chunk_content(self, chunkurl):
        "Liefert die Chunk-Content."
        return urllib2.urlopen(chunkurl).read()

    def _get_sequence_nr(self, chunkcontent):
        "Liefert die aktuelle Sequenzummer."
        return int(re.findall(r'EXT-X-MEDIA-SEQUENCE:(\d*)', chunkcontent)[0])

    def _get_mediabase(self, streambase, chunkcontent):
        "Liefert die Basis-URL zum Chunk."
        name = re.findall(r'(media_w.*?_)', chunkcontent)[0]
        return "%s%s" % (streambase, name)
