# -*- coding: utf-8 -*-
#
# Picard, the next-generation MusicBrainz tagger
# Copyright (C) 2012 Michael Wiencek
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

import traceback
from collections import defaultdict
from functools import partial
from itertools import combinations
from PyQt4 import QtCore
from picard import config, log
from picard.metadata import Metadata
from picard.dataobj import DataObject
from picard.mbxml import media_formats_from_node, label_info_from_node


class ReleaseGroup(DataObject):

    def __init__(self, id):
        DataObject.__init__(self, id)
        self.metadata = Metadata()
        self.loaded = False
        self.versions = []
        self.loaded_albums = set()
        self.refcount = 0

    def load_versions(self, callback):
        kwargs = {"release-group": self.id, "limit": 100}
        self.tagger.xmlws.browse_releases(partial(self._request_finished, callback), **kwargs)

    def _parse_versions(self, document):
        """Parse document and return a list of releases"""
        del self.versions[:]
        release_data = []

        for node in document.metadata[0].release_list[0].release:
            labels, catnums = label_info_from_node(node.label_info_list[0])
            release_data.append({
                "id":      node.id,
                "date":    node.date[0].text if "date" in node.children else "",
                "country": node.country[0].text if "country" in node.children else "",
                "format":  media_formats_from_node(node.medium_list[0]),
                "labels":  ", ".join(set(labels)),
                "catnums": ", ".join(set(catnums)),
                "tracks":  " + ".join([m.track_list[0].count for m in node.medium_list[0].medium]),

                # extra information, only used for diambiguation
                "packaging": node.packaging[0].text \
                            if "packaging" in node.children else None,

                "barcode": (node.barcode[0].text or _("[no barcode]")) \
                            if "barcode" in node.children else None,

                "comment": node.disambiguation[0].text \
                            if "disambiguation" in node.children else None,
            })

        release_data.sort(key=lambda x: x["date"])
        keys = ("date", "country", "labels", "catnums", "tracks", "format")
        extra_keys = ("packaging", "barcode", "comment")
        version_names_dupes = defaultdict(list)

        for data in release_data:
            name = " / ".join(filter(None, (data[k] for k in keys))).replace("&", "&&")
            if name == data["tracks"]:
                name = "%s / %s" % (_('[no release info]'), name)
            version = {"id": data["id"], "name": name, "data": data}
            version_names_dupes[name].append(version)
            self.versions.append(version)

        for name, dupes in version_names_dupes.iteritems():
            for a, b in combinations(dupes, 2):
                for key in extra_keys:
                    (value1, value2) = (a["data"][key], b["data"][key])
                    if value1 != value2:
                        if value1 and value1 not in a["name"]:
                            a["name"] += " / " + value1.replace("&", "&&")
                        if value2 and value2 not in b["name"]:
                            b["name"] += " / " + value2.replace("&", "&&")

    def _request_finished(self, callback, document, http, error):
        try:
            if error:
                log.error("%r", unicode(http.errorString()))
            else:
                try:
                    self._parse_versions(document)
                except:
                    error = True
                    log.error(traceback.format_exc())
        finally:
            self.loaded = True
            callback()

    def remove_album(self, id):
        self.loaded_albums.discard(id)
        self.refcount -= 1
        if self.refcount == 0:
            del self.tagger.release_groups[self.id]
