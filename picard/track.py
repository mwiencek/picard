# -*- coding: utf-8 -*-
#
# Picard, the next-generation MusicBrainz tagger
# Copyright (C) 2004 Robert Kaye
# Copyright (C) 2006 Lukáš Lalinský
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

from picard.metadata import Metadata, run_track_metadata_processors
from picard.dataobj import DataObject
from picard.util import asciipunct, partial
from picard.mbxml import recording_to_metadata
from picard.script import ScriptParser
from picard.const import VARIOUS_ARTISTS_ID
from picard.ui.itemmodels import TrackItem
import traceback


_TRANSLATE_TAGS = {
    "hip hop": u"Hip-Hop",
    "synth-pop": u"Synthpop",
    "electronica": u"Electronic",
}


class Track(TrackItem, DataObject):

    def __init__(self, id, album):
        TrackItem.__init__(self)
        DataObject.__init__(self, id)
        self.album = album
        self.linked_file = None

    def __repr__(self):
        return '<Track %s %r>' % (self.id, self.metadata["title"])

    def add_file(self, file):
        if self.linked_file:
            self.linked_file.move(self.tagger.unmatched_files)
        self.linked_file = file
        self.album._files += 1
        self.update_file_metadata(file)

    def update_file_metadata(self, file):
        file.copy_metadata(self.metadata)
        file.update()
        self.update()

    def remove_file(self, file):
        if file is self.linked_file:
            self.linked_file = None
            self.album._files -= 1
            file.copy_metadata(file.orig_metadata)
            self.update()

    def iterfiles(self):
        if self.linked_file:
            yield self.linked_file

    @property
    def linked_files(self):
        return [self.linked_file] if self.linked_file else []

    def is_linked(self):
        return self.linked_file is not None

    def _customize_metadata(self):
        tm = self.metadata

        # Custom VA name
        if tm['musicbrainz_artistid'] == VARIOUS_ARTISTS_ID:
            tm['artistsort'] = tm['artist'] = self.config.setting['va_name']

        if self.config.setting['folksonomy_tags']:
            self._convert_folksonomy_tags_to_genre()

        # Convert Unicode punctuation
        if self.config.setting['convert_punctuation']:
            tm.apply_func(asciipunct)

    def _convert_folksonomy_tags_to_genre(self):
        # Combine release and track tags
        album = self.album
        tags = dict(self.folksonomy_tags)
        self.merge_folksonomy_tags(tags, album.folksonomy_tags)
        if album.release_group:
            self.merge_folksonomy_tags(tags, album.release_group.folksonomy_tags)
        if not tags:
            return
        # Convert counts to values from 0 to 100
        maxcount = max(tags.values())
        taglist = []
        for name, count in tags.items():
            taglist.append((100 * count / maxcount, name))
        taglist.sort(reverse=True)
        # And generate the genre metadata tag
        maxtags = self.config.setting['max_tags']
        minusage = self.config.setting['min_tag_usage']
        ignore_tags = self.config.setting['ignore_tags']
        genre = []
        for usage, name in taglist[:maxtags]:
            if name in ignore_tags:
                continue
            if usage < minusage:
                break
            name = _TRANSLATE_TAGS.get(name, name.title())
            genre.append(name)
        join_tags = self.config.setting['join_tags']
        if join_tags:
            genre = [join_tags.join(genre)]
        self.metadata['genre'] = genre

    def remove(self):
        if self.linked_file:
            self.linked_file.remove()


class NonAlbumTrack(Track):

    can_refresh = True

    def __init__(self, id):
        Track.__init__(self, id, None)
        self.album = self.tagger.nats
        self.callback = None
        self.loaded = False

    def column(self, column):
        if column == "title":
            return self.metadata["title"]
        return Track.column(self, column)

    def load(self):
        self.metadata.copy(self.album.metadata)
        self.metadata["title"] = _(u"[loading track information]")
        self.loaded = False
        self.album.update()
        mblogin = False
        inc = ["artist-credits", "artists", "aliases"]
        if self.config.setting["track_ars"]:
            inc += ["artist-rels", "url-rels", "recording-rels",
                    "work-rels", "work-level-rels"]
        if self.config.setting["folksonomy_tags"]:
            if self.config.setting["only_my_tags"]:
                mblogin = True
                inc += ["user-tags"]
            else:
                inc += ["tags"]
        if self.config.setting["enable_ratings"]:
            mblogin = True
            inc += ["user-ratings"]
        self.tagger.xmlws.get_track_by_id(self.id,
            partial(self._recording_request_finished), inc, mblogin=mblogin)

    def _recording_request_finished(self, document, http, error):
        if error:
            self.log.error("%r", unicode(http.errorString()))
            return
        try:
            recording = document.metadata[0].recording[0]
            self._parse_recording(recording)
            if self.linked_file:
                self.update_file_metadata(self.linked_file)
        except:
            self.log.error(traceback.format_exc())

    def _parse_recording(self, recording):
        recording_to_metadata(recording, self, self.config)
        self._customize_metadata()
        m = self.metadata
        run_track_metadata_processors(self.album, m, None, recording)
        if self.config.setting["enable_tagger_script"]:
            script = self.config.setting["tagger_script"]
            if script:
                parser = ScriptParser()
                try:
                    parser.eval(script, m)
                except:
                    self.log.error(traceback.format_exc())
                m.strip_whitespace()
        self.loaded = True
        if self.callback:
            self.callback()
            self.callback = None
        self.album.update()

    def run_when_loaded(self, func):
        if self.loaded:
            func()
        else:
            self.callback = func
