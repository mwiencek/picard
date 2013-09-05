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
from functools import partial
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

    def _version_names_dupes(self, versions):
        """Find releases with conflicting names"""
        dupes = dict()
        length = len(versions)
        for i in range(0, length):
            for j in range(i + 1, length):
                name = versions[i]['name']
                if name == versions[j]['name']:
                    if versions[i]['extras'] != versions[j]['extras']:
                        if name not in dupes:
                            dupes[name] = []
                        dupes[name].append((i, j))
        return dupes

    def _versions_disambiguation(self, versions):
        """Find elements in extra information that may help to disambiguate"""

        def _append_diff(diff, index, s):
            if index not in diff:
                diff[index] = []
            if s not in diff[index]:
                diff[index].append(s)

        disambiguates = dict()
        for name, dupes in self._version_names_dupes(versions).iteritems():
            diff = dict()
            for a_index, b_index in dupes:
                a = versions[a_index]['extras']
                b = versions[b_index]['extras']
                for e in a:
                    if e not in b:
                        _append_diff(diff, a_index, a[e])
                    else:
                        if a[e] != b[e]:
                            _append_diff(diff, a_index, a[e])
                            _append_diff(diff, b_index, b[e])
            disambiguates[name] = diff
        disambiguation_list = dict()
        for name in disambiguates:
            for i in disambiguates[name]:
                disambiguation_list[i] = disambiguates[name][i]
        return disambiguation_list

    def _parse_versions(self, document):
        """Parse document and return a list of releases"""
        del self.versions[:]
        data = []

        for node in document.metadata[0].release_list[0].release:
            labels, catnums = label_info_from_node(node.label_info_list[0])
            release = {
                "id":      node.id,
                "date":    node.date[0].text if "date" in node.children else "",
                "country": node.country[0].text if "country" in node.children else "",
                "format":  media_formats_from_node(node.medium_list[0]),
                "labels":  ", ".join(set(labels)),
                "catnums": ", ".join(set(catnums)),
                "tracks":  " + ".join([m.track_list[0].count for m in node.medium_list[0].medium]),
            }
            if "barcode" in node.children:
                barcode = node.barcode[0].text
                if barcode == "":
                    barcode = "[none]"
                release['barcode'] = barcode
            if "packaging" in node.children:
                release['packaging'] = node.packaging[0].text
            if "disambiguation" in node.children:
                release['disambiguation'] = node.disambiguation[0].text
            data.append(release)
        data.sort(key=lambda x: x["date"])
        keys = ("date", "country", "labels", "catnums", "tracks", "format")
        extrakeys = ("packaging", "barcode", "disambiguation")

        for version in data:
            name = " / ".join(filter(None, (version[k] for k in keys))).replace("&", "&&")
            extras = dict()
            if name == version["tracks"]:
                name = "%s / %s" % (_('[no release info]'), name)
            else:
                for k in extrakeys:
                    if k in version:
                        extras[k] = version[k]
            self.versions.append({"id": version["id"], "name": name, "extras": extras})

    def _versions_list(self):
        """Add disambiguation information to releases list names"""
        disambiguation_list = self._versions_disambiguation(self.versions)
        for i, version in enumerate(self.versions):
            if i in disambiguation_list:
                version['name'] += " / " + " / ".join(disambiguation_list[i]).replace("&", "&&")
            del version['extras']

    def _other_versions(self, document):
        """Returns a list of disambiguated releases for the user to choose from"""
        self._parse_versions(document)
        self._versions_list()

    def _request_finished(self, callback, document, http, error):
        try:
            if error:
                log.error("%r", unicode(http.errorString()))
            else:
                try:
                    self._other_versions(document)
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
