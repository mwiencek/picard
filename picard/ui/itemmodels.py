# -*- coding: utf-8 -*-
#
# Picard, the next-generation MusicBrainz tagger
# Copyright (C) 2006 Lukáš Lalinský
# Copyright (C) 2013 Michael Wiencek
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

import os
import re
from PyQt4 import QtCore, QtGui
from picard.util import encode_filename, format_time
from picard.ui.treemodel import TreeModel, TreeItem


class BaseTreeModel(TreeModel):

    columns = [
        (N_('Title'), 'title'),
        (N_('Length'), '~length'),
        (N_('Artist'), 'artist'),
    ]

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            return self.columns[section][0]
        return None

    def data(self, index, role):
        if not index.isValid():
            return None
        Qt = QtCore.Qt
        item = self.itemFromIndex(index)
        if role == Qt.DisplayRole:
            return item.column(self.columns[index.column()][1])
        elif role == Qt.ForegroundRole:
            return item._foreground_color
        elif role == Qt.BackgroundRole:
            return item._background_color
        elif role == Qt.DecorationRole and index.column() == 0:
            return item._icon
        return None

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def mimeTypes(self):
        """List of MIME types accepted by this view."""
        return ["text/uri-list", "application/picard.album-list"]

    def dropMimeData(self, data, action, row, column, parent):
        target = self.itemFromIndex(parent) or self.tagger.unmatched_files
        handled = False
        # text/uri-list
        urls = data.urls()
        if urls:
            self.drop_urls(urls, target)
            handled = True
        # application/picard.album-list
        albums = data.data("application/picard.album-list")
        if albums:
            albums = [self.tagger.load_album(id) for id in str(albums).split("\n")]
            target.drop_files(self.tagger.get_files_from_objects(albums))
            handled = True
        return handled

    def drop_urls(self, urls, target):
        files = []
        new_files = []
        for url in urls:
            if url.scheme() == "file" or not url.scheme():
                # Dropping a file from iTunes gives a filename with a NULL terminator
                filename = os.path.normpath(os.path.realpath(unicode(url.toLocalFile()).rstrip("\0")))
                file = self.tagger.files.get(filename)
                if file:
                    files.append(file)
                elif os.path.isdir(encode_filename(filename)):
                    self.tagger.add_directory(filename)
                else:
                    new_files.append(filename)
            elif url.scheme() in ("http", "https"):
                path = unicode(url.path())
                match = re.search(r"/(release|recording)/([0-9a-z\-]{36})", path)
                if match:
                    entity = match.group(1)
                    mbid = match.group(2)
                    if entity == "release":
                        self.tagger.load_album(mbid)
                    elif entity == "recording":
                        self.tagger.load_nat(mbid)
        target.drop_files(files)
        if new_files:
            self.tagger.add_files(new_files, target=target)


class ClusterItem(TreeItem):

    can_remove = True
    can_edit_tags = True
    can_autotag = True

    def drop_files(self, files):
        for file in files:
            file.move(self)

    def column(self, column):
        if column == 'title':
            return '%s (%d)' % (self.metadata['album'], len(self.files))
        elif column == '~length':
            return format_time(self.metadata.length)
        elif column == 'artist':
            return self.metadata['albumartist']
        return self.metadata[column]

    def browser_lookup(self):
        metadata = self.metadata
        self.get_file_lookup().tagLookup(
                metadata["albumartist"], metadata["album"], metadata["title"],
                metadata["tracknumber"], "", "")

    @property
    def can_save(self):
        return bool(self.files)

    @property
    def can_analyze(self):
        return any(file.can_analyze for file in self.files)


class AlbumItem(TreeItem):

    can_remove = True
    can_edit_tags = True
    can_refresh = True

    def update(self, update_tracks=True):
        if update_tracks:
            self.replaceChildren(self.tracks)
        self._icon = AlbumItem._icon_saved if self.is_complete() else AlbumItem._icon
        TreeItem.update(self)

    def drop_files(self, files):
        self.match_files(files, unmatched=False)

    def column(self, column):
        if column == 'title':
            if self.tracks:
                matched_tracks = self.get_num_matched_tracks()
                text = u'%s\u200E (%d/%d' % (self.metadata['album'], matched_tracks, len(self.tracks))
                unsaved = self.get_num_unsaved_files()
                if unsaved:
                    text += '; %d*' % (unsaved,)
                text += ungettext("; %i image", "; %i images",
                        len(self.metadata.images)) % len(self.metadata.images)
                return text + ')'
            else:
                return self.metadata['album']
        elif column == '~length':
            length = self.metadata.length
            if length:
                return format_time(length)
            else:
                return ''
        elif column == 'artist':
            return self.metadata['albumartist']
        return ''

    def browser_lookup(self):
        albumid = self.metadata["musicbrainz_albumid"]
        if albumid:
            self.tagger.get_file_lookup().albumLookup(albumid)

    @property
    def can_save(self):
        return self._files > 0


class TrackItem(TreeItem):

    can_edit_tags = True

    def update(self, update_album=True):
        file = self.linked_file
        if file:
            if file.state == file.NORMAL:
                self._icon = FileItem._icon_saved
            elif file.state == file.PENDING:
                self._icon = FileItem._match_pending_icons[int(file.similarity * 5 + 0.5)]
            else:
                self._icon = FileItem._match_icons[int(file.similarity * 5 + 0.5)]
            self._foreground_color = TrackItem._track_colors[file.state]
            self._background_color = get_match_color(file.similarity, TreeItem._background_color)
        else:
            self._foreground_color = TreeItem._foreground_color
            self._background_color = get_match_color(1, TreeItem._background_color)
            self._icon = TrackItem._icon
        TreeItem.update(self)
        if update_album:
            AlbumItem.update(self.album, update_tracks=False)

    def drop_files(self, files):
        files[0].move(self) if len(files) == 1 else self.album.drop_files(files)

    def column(self, column):
        m = self.metadata
        if column == 'title':
            prefix = "%s-" % m['discnumber'] if m['discnumber'] and m['totaldiscs'] != "1" else ""
            return u"%s%s  %s" % (prefix, m['tracknumber'].zfill(2), m['title'])
        return m[column]

    def browser_lookup(self):
        trackid = metadata["musicbrainz_trackid"]
        if trackid:
            self.tagger.get_file_lookup().trackLookup(trackid)

    @property
    def can_save(self):
        return self.linked_file.can_save if self.linked_file else False

    @property
    def can_remove(self):
        return self.linked_file.can_remove if self.linked_file else False

    @property
    def can_view_info(self):
        return self.is_linked()


class FileItem(TreeItem):

    can_save = True
    can_remove = True
    can_edit_tags = True
    can_analyze = True
    can_autotag = True
    can_view_info = True
    can_browser_lookup = True

    def update(self):
        if self.state == self.ERROR:
            self._icon = FileItem._icon_error
        elif self.state == self.PENDING:
            self._icon = FileItem._icon_pending
        else:
            self._icon = FileItem._icon
        self._foreground_color = FileItem._file_colors[self.state]
        self._background_color = get_match_color(self.similarity, TreeItem._background_color)
        TreeItem.update(self)

    def drop_files(self, files):
        self.parentItem().drop_files(files)

    def column(self, column):
        if column == "title" and not self.metadata["title"]:
            return self.base_filename
        return self.metadata[column]

    def browser_lookup(self):
        metadata = self.metadata
        self.tagger.get_file_lookup().tagLookup(
                metadata["artist"], metadata["album"], metadata["title"],
                metadata["tracknumber"], str(metadata.length), self.filename)


def get_match_color(similarity, basecolor):
    c1 = (basecolor.red(), basecolor.green(), basecolor.blue())
    c2 = (223, 125, 125)
    return QtGui.QColor(
        c2[0] + (c1[0] - c2[0]) * similarity,
        c2[1] + (c1[1] - c2[1]) * similarity,
        c2[2] + (c1[2] - c2[2]) * similarity)
