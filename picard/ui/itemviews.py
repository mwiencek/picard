# -*- coding: utf-8 -*-
#
# Picard, the next-generation MusicBrainz tagger
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

from PyQt4 import QtCore, QtGui
from picard.album import Album, NatAlbum
from picard.cluster import Cluster, ClusterList, UnmatchedFiles
from picard.file import File
from picard.track import Track, NonAlbumTrack
from picard.util import icontheme, partial
from picard.config import Option, TextOption
from picard.plugin import ExtensionPoint
from picard.ui.ratingwidget import RatingWidget
from picard.ui.collectionmenu import CollectionMenu
from picard.ui.itemmodels import *


class BaseAction(QtGui.QAction):
    NAME = "Unknown"
    MENU = []

    def __init__(self):
        QtGui.QAction.__init__(self, self.NAME, None)
        self.triggered.connect(self.__callback)

    def __callback(self):
        objs = self.tagger.window.panel.selected_objects()
        self.callback(objs)

    def callback(self, objs):
        raise NotImplementedError


_album_actions = ExtensionPoint()
_cluster_actions = ExtensionPoint()
_clusterlist_actions = ExtensionPoint()
_track_actions = ExtensionPoint()
_file_actions = ExtensionPoint()

def register_album_action(action):
    _album_actions.register(action.__module__, action)

def register_cluster_action(action):
    _cluster_actions.register(action.__module__, action)

def register_clusterlist_action(action):
    _clusterlist_actions.register(action.__module__, action)

def register_track_action(action):
    _track_actions.register(action.__module__, action)

def register_file_action(action):
    _file_actions.register(action.__module__, action)


class MainPanel(QtGui.QSplitter):

    options = [
        Option("persist", "splitter_state", QtCore.QByteArray(), QtCore.QVariant.toByteArray),
    ]

    def __init__(self, window, parent=None):
        QtGui.QSplitter.__init__(self, parent)
        self.window = window
        self.create_icons()

        TreeItem.window = window
        TreeItem.panel = self

        TreeItem._background_color = self.palette().base().color()
        TreeItem._foreground_color = self.palette().text().color()
        TrackItem._track_colors = {
            File.NORMAL: self.config.setting["color_saved"],
            File.CHANGED: TreeItem._foreground_color,
            File.PENDING: self.config.setting["color_pending"],
            File.ERROR: self.config.setting["color_error"],
        }
        FileItem._file_colors = {
            File.NORMAL: TreeItem._foreground_color,
            File.CHANGED: self.config.setting["color_modified"],
            File.PENDING: self.config.setting["color_pending"],
            File.ERROR: self.config.setting["color_error"],
        }

        self.file_view = FileTreeView(window, self)
        self.album_view = AlbumTreeView(window, self)
        self._selected_view = self.file_view

    def save_state(self):
        self.config.persist["splitter_state"] = self.saveState()
        self.file_view.save_state()
        self.album_view.save_state()

    def restore_state(self):
        self.restoreState(self.config.persist["splitter_state"])

    def create_icons(self):
        if hasattr(QtGui.QStyle, 'SP_DirIcon'):
            ClusterItem._icon = self.style().standardIcon(QtGui.QStyle.SP_DirIcon)
        else:
            ClusterItem._icon = icontheme.lookup('folder', icontheme.ICON_SIZE_MENU)

        ClusterList._icon = ClusterItem._icon
        AlbumItem._icon = icontheme.lookup('media-optical', icontheme.ICON_SIZE_MENU)
        AlbumItem._icon_saved = icontheme.lookup('media-optical-saved', icontheme.ICON_SIZE_MENU)
        TrackItem._icon = QtGui.QIcon(":/images/note.png")
        FileItem._icon = QtGui.QIcon(":/images/file.png")
        FileItem._icon_pending = QtGui.QIcon(":/images/file-pending.png")
        FileItem._icon_error = icontheme.lookup('dialog-error', icontheme.ICON_SIZE_MENU)
        FileItem._icon_saved = QtGui.QIcon(":/images/track-saved.png")

        FileItem._match_icons = [
            QtGui.QIcon(":/images/match-50.png"),
            QtGui.QIcon(":/images/match-60.png"),
            QtGui.QIcon(":/images/match-70.png"),
            QtGui.QIcon(":/images/match-80.png"),
            QtGui.QIcon(":/images/match-90.png"),
            QtGui.QIcon(":/images/match-100.png"),
        ]
        FileItem._match_pending_icons = [
            QtGui.QIcon(":/images/match-pending-50.png"),
            QtGui.QIcon(":/images/match-pending-60.png"),
            QtGui.QIcon(":/images/match-pending-70.png"),
            QtGui.QIcon(":/images/match-pending-80.png"),
            QtGui.QIcon(":/images/match-pending-90.png"),
            QtGui.QIcon(":/images/match-pending-100.png"),
        ]
        self.icon_plugins = icontheme.lookup('applications-system', icontheme.ICON_SIZE_MENU)

    def update_selection(self, view):
        if self._selected_view != view:
            self._selected_view.clearSelection()
            self._selected_view = view
        self.window.update_selection([view.model.itemFromIndex(index)
            for index in view.selectionModel().selectedRows()])

    def remove(self, objects):
        for obj in objects:
            obj.remove()
        index = self._selected_view.currentIndex()
        if index.isValid():
            # select the current index
            self._selected_view.setCurrentIndex(index)
        else:
            self.update_selection(self._selected_view)


class BaseTreeView(QtGui.QTreeView):

    options = [
        Option("setting", "color_modified", QtGui.QColor(QtGui.QPalette.WindowText), QtGui.QColor),
        Option("setting", "color_saved", QtGui.QColor(0, 128, 0), QtGui.QColor),
        Option("setting", "color_error", QtGui.QColor(200, 0, 0), QtGui.QColor),
        Option("setting", "color_pending", QtGui.QColor(128, 128, 128), QtGui.QColor),
    ]

    selection_changed = QtCore.pyqtSignal(QtGui.QTreeView)

    def __init__(self, model, window, parent=None):
        QtGui.QTreeView.__init__(self, parent)

        self.model = model
        self.setModel(model)
        model.itemExpanded.connect(self.item_expanded)
        model.itemHidden.connect(self.item_hidden)
        model.dataChanged.connect(self.data_changed)

        self.window = window
        self.panel = parent

        self.numHeaderSections = len(BaseTreeModel.columns)
        self.restore_state()

        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setUniformRowHeights(True)

        # enable sorting, but don't actually use it by default
        self.header().setSortIndicator(-1, QtCore.Qt.AscendingOrder)
        self.setSortingEnabled(True)

        self.expand_all_action = QtGui.QAction(_("&Expand all"), self)
        self.expand_all_action.triggered.connect(self.expandAll)
        self.collapse_all_action = QtGui.QAction(_("&Collapse all"), self)
        self.collapse_all_action.triggered.connect(self.collapseAll)
        self.doubleClicked.connect(self.activate_item)

    def itemAtPos(self, pos):
        index = self.indexAt(pos)
        if index.isValid():
            return self.model.itemFromIndex(index)

    def contextMenuEvent(self, event):
        item = self.itemAtPos(event.pos())
        if not item:
            return
        plugin_actions = None
        can_view_info = self.window.view_info_action.isEnabled()
        menu = QtGui.QMenu(self)

        if isinstance(item, Track):
            if can_view_info:
                menu.addAction(self.window.view_info_action)
            plugin_actions = list(_track_actions)
            if item.linked_file:
                menu.addAction(self.window.open_file_action)
                menu.addAction(self.window.open_folder_action)
                plugin_actions.extend(_file_actions)
            menu.addAction(self.window.browser_lookup_action)
            menu.addSeparator()
            if isinstance(item, NonAlbumTrack):
                menu.addAction(self.window.refresh_action)
        elif isinstance(item, Cluster):
            menu.addAction(self.window.browser_lookup_action)
            menu.addSeparator()
            menu.addAction(self.window.autotag_action)
            menu.addAction(self.window.analyze_action)
            if isinstance(item, UnmatchedFiles):
                menu.addAction(self.window.cluster_action)
            plugin_actions = list(_cluster_actions)
        elif isinstance(item, ClusterList):
            menu.addAction(self.window.autotag_action)
            menu.addAction(self.window.analyze_action)
            plugin_actions = list(_clusterlist_actions)
        elif isinstance(item, File):
            if can_view_info:
                menu.addAction(self.window.view_info_action)
            menu.addAction(self.window.open_file_action)
            menu.addAction(self.window.open_folder_action)
            menu.addAction(self.window.browser_lookup_action)
            menu.addSeparator()
            menu.addAction(self.window.autotag_action)
            menu.addAction(self.window.analyze_action)
            plugin_actions = list(_file_actions)
        elif isinstance(item, Album):
            menu.addAction(self.window.browser_lookup_action)
            menu.addSeparator()
            menu.addAction(self.window.refresh_action)
            plugin_actions = list(_album_actions)

        menu.addAction(self.window.save_action)
        menu.addAction(self.window.remove_action)

        bottom_separator = False

        if isinstance(item, Album) and not isinstance(item, NatAlbum) and item.loaded:
            releases_menu = QtGui.QMenu(_("&Other versions"), menu)
            menu.addSeparator()
            menu.addMenu(releases_menu)
            loading = releases_menu.addAction(_('Loading...'))
            loading.setEnabled(False)
            bottom_separator = True

            def _add_other_versions():
                releases_menu.removeAction(loading)
                for version in item.release_group.versions:
                    action = releases_menu.addAction(version["name"])
                    action.setCheckable(True)
                    if item.id == version["id"]:
                        action.setChecked(True)
                    action.triggered.connect(partial(item.switch_release_version, version["id"]))

            _add_other_versions() if item.release_group.loaded else \
                item.release_group.load_versions(_add_other_versions)

        if self.config.setting["enable_ratings"] and \
           len(self.window.selected_objects) == 1 and isinstance(item, Track):
            menu.addSeparator()
            action = QtGui.QWidgetAction(menu)
            action.setDefaultWidget(RatingWidget(menu, item))
            menu.addAction(action)
            menu.addSeparator()

        selected_albums = [a for a in self.window.selected_objects if type(a) == Album]
        if selected_albums:
            if not bottom_separator:
                menu.addSeparator()
            menu.addMenu(CollectionMenu(selected_albums, _("Collections"), menu))

        if plugin_actions:
            plugin_menu = QtGui.QMenu(_("&Plugins"), menu)
            plugin_menu.setIcon(self.panel.icon_plugins)
            menu.addSeparator()
            menu.addMenu(plugin_menu)

            plugin_menus = {}
            for action in plugin_actions:
                action_menu = plugin_menu
                for index in xrange(1, len(action.MENU)):
                    key = tuple(action.MENU[:index])
                    try:
                        action_menu = plugin_menus[key]
                    except KeyError:
                        action_menu = plugin_menus[key] = action_menu.addMenu(key[-1])
                action_menu.addAction(action)

        if isinstance(item, (Cluster, ClusterList, Album)):
            menu.addSeparator()
            menu.addAction(self.expand_all_action)
            menu.addAction(self.collapse_all_action)

        menu.exec_(event.globalPos())
        event.accept()

    def restore_state(self):
        sizes = self.config.persist[self.view_sizes.name]
        header = self.header()
        sizes = sizes.split(" ")
        try:
            for i in range(self.numHeaderSections - 1):
                header.resizeSection(i, int(sizes[i]))
        except IndexError:
            pass

    def save_state(self):
        cols = range(self.numHeaderSections - 1)
        sizes = " ".join(str(self.header().sectionSize(i)) for i in cols)
        self.config.persist[self.view_sizes.name] = sizes

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.accept()

    def startDrag(self, supportedActions):
        """Start drag, *without* using pixmap."""
        items = self.window.selected_objects
        if items:
            drag = QtGui.QDrag(self)
            drag.setMimeData(self.mimeData(items))
            drag.start(supportedActions)

    def mimeData(self, items):
        """Return MIME data for specified items."""
        album_ids = []
        files = []
        url = QtCore.QUrl.fromLocalFile
        for item in items:
            if isinstance(item, Album):
                album_ids.append(str(item.id))
            elif isinstance(item, Track):
                if item.linked_file:
                    files.append(url(item.linked_file.filename))
            elif isinstance(item, File):
                files.append(url(item.filename))
            elif isinstance(item, Cluster):
                files.extend(url(file.filename) for file in item.files)
            elif isinstance(item, ClusterList):
                files.extend(url(file.filename) for file in item.iterfiles())
        mimeData = QtCore.QMimeData()
        mimeData.setData("application/picard.album-list", "\n".join(album_ids))
        if files:
            mimeData.setUrls(files)
        return mimeData

    def dropEvent(self, event):
        return QtGui.QTreeView.dropEvent(self, event)

    def selectionChanged(self, selected, deselected):
        QtGui.QTreeView.selectionChanged(self, selected, deselected)
        self.panel.update_selection(self)

    def activate_item(self, index):
        item = self.model.itemFromIndex(index)
        if item.can_view_info:
            self.window.view_info()

    def item_expanded(self, index, expanded):
        self.setExpanded(index, expanded)

    def item_hidden(self, index, hidden):
        self.setHidden(index, hidden)

    def data_changed(self, topLeft, bottomRight):
        if self.selectionModel().selection().contains(topLeft):
            self.window.update_selection()


class FileTreeView(BaseTreeView):

    view_sizes = TextOption("persist", "file_view_sizes", "250 40 100")

    def __init__(self, window, parent=None):
        BaseTreeView.__init__(self, FileTreeModel(), window, parent)
        self.model.appendItem(self.tagger.unmatched_files, None)
        self.model.appendItem(self.tagger.clusters, None)
        self.tagger.unmatched_files.setExpanded(True)
        self.tagger.clusters.setExpanded(True)


class AlbumTreeView(BaseTreeView):

    view_sizes = TextOption("persist", "album_view_sizes", "250 40 100")

    def __init__(self, window, parent=None):
        BaseTreeView.__init__(self, BaseTreeModel(), window, parent)
        self.tagger.album_added.connect(self.add_album)
        self.tagger.album_removed.connect(self.model.removeItem)

    def add_album(self, album):
        self.model.appendItem(album, None)
