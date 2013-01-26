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

import os
import re
from operator import itemgetter
from heapq import heappush, heappop
from UserDict import UserDict
from PyQt4 import QtCore
from picard.metadata import Metadata
from picard.similarity import similarity2, similarity
from picard.ui.itemmodels import TreeItem, ClusterItem
from picard.util import format_time
from picard.mbxml import artist_credit_from_node


class Cluster(ClusterItem):

    PENDING = 0
    NORMAL = 1
    REMOVED = 2

    # Weights for different elements when comparing a cluster to a release
    comparison_weights = {
        'album': 17,
        'albumartist': 6,
        'totaltracks': 5,
        'releasecountry': 2,
        'format': 2,
    }

    def __init__(self, name, artist=""):
        super(Cluster, self).__init__()
        self.metadata = Metadata()
        self.metadata['album'] = name
        self.metadata['albumartist'] = artist
        self.metadata['totaltracks'] = 0
        self.key = (name, artist)
        self.files = []
        self.lookup_task = None
        self.state = Cluster.NORMAL

    def __repr__(self):
        return '<Cluster %r>' % self.metadata['album']

    def __len__(self):
        return len(self.files)

    def add_file(self, file):
        self.files.append(file)
        self.appendChild(file)
        self.metadata.length += file.metadata.length
        self.metadata["totaltracks"] = len(self.files)
        file.update()
        ClusterItem.update(self)

    def remove_file(self, file):
        self.files.remove(file)
        self.removeChild(file)
        self.metadata.length -= file.metadata.length
        self.metadata["totaltracks"] = len(self.files)
        ClusterItem.update(self)
        if not len(self):
            self.remove()

    def iterfiles(self):
        for file in self.files:
            yield file

    def update(self):
        key = (self.metadata["album"], self.metadata["albumartist"])
        if self.key != key:
            self.tagger.clusters[key] = self.tagger.clusters.pop(self.key)
            self.key = key
        ClusterItem.update(self)

    def remove(self):
        self.log.debug("Removing %r", self)
        self.state = Cluster.REMOVED
        self.clear_lookup_task()
        for file in self.files:
            file.remove(from_parent=False)
        del self.tagger.clusters[self.key]
        self.tagger.clusters.removeChild(self)

    def _lookup_finished(self, document, http, error):
        if self.state == Cluster.REMOVED:
            return

        self.lookup_task = None
        self.state = Cluster.NORMAL
        ClusterItem.update(self)

        try:
            releases = document.metadata[0].release_list[0].release
        except (AttributeError, IndexError):
            releases = None

        # no matches
        if not releases:
            self.tagger.window.set_statusbar_message(N_("No matching releases for cluster %s"), self.metadata['album'], timeout=3000)
            return

        # multiple matches -- calculate similarities to each of them
        match = sorted((self.metadata.compare_to_release(
            release, Cluster.comparison_weights) for release in releases),
            reverse=True, key=itemgetter(0))[0]

        if match[0] < self.config.setting['cluster_lookup_threshold']:
            self.tagger.window.set_statusbar_message(N_("No matching releases for cluster %s"), self.metadata['album'], timeout=3000)
            return
        self.tagger.window.set_statusbar_message(N_("Cluster %s identified!"), self.metadata['album'], timeout=3000)
        self.tagger.load_album(match[1].id).match_files(self.files)

    def lookup_metadata(self):
        """ Try to identify the cluster using the existing metadata. """
        self.tagger.window.set_statusbar_message(N_("Looking up the metadata for cluster %s..."), self.metadata['album'])
        self.state = Cluster.PENDING
        ClusterItem.update(self)
        self.lookup_task = self.tagger.xmlws.find_releases(
                self._lookup_finished,
                artist=self.metadata['albumartist'],
                release=self.metadata['album'],
                tracks=str(len(self.files)),
                limit=25)

    def clear_lookup_task(self):
        if self.lookup_task:
            self.tagger.xmlws.remove_task(self.lookup_task)
            self.lookup_task = None

    @staticmethod
    def cluster(files, threshold):
        artistDict = ClusterDict()
        albumDict = ClusterDict()
        tracks = []
        for file in files:
            artist = file.metadata["artist"]
            album = file.metadata["album"] or os.path.basename(os.path.dirname(file.filename))
            # For each track, record the index of the artist and album within the clusters
            tracks.append((artistDict.add(artist), albumDict.add(album)))

        artist_cluster_engine = ClusterEngine(artistDict)
        artist_cluster = artist_cluster_engine.cluster(threshold)

        album_cluster_engine = ClusterEngine(albumDict)
        album_cluster = album_cluster_engine.cluster(threshold)

        # Arrange tracks into albums
        albums = {}
        for i in xrange(len(tracks)):
            cluster = album_cluster_engine.getClusterFromId(tracks[i][1])
            if cluster is not None:
                albums.setdefault(cluster, []).append(i)

        # Now determine the most prominent names in the cluster and build the
        # final cluster list
        for album_id, album in albums.items():
            album_name = album_cluster_engine.getClusterTitle(album_id)

            artist_max = 0
            artist_id = None
            artist_hist = {}
            for track_id in album:
                cluster = artist_cluster_engine.getClusterFromId(
                     tracks[track_id][0])
                cnt = artist_hist.get(cluster, 0) + 1
                if cnt > artist_max:
                    artist_max = cnt
                    artist_id = cluster
                artist_hist[cluster] = cnt

            if artist_id is None:
                artist_name = u"Various Artists"
            else:
                artist_name = artist_cluster_engine.getClusterTitle(artist_id)

            yield album_name, artist_name, (files[i] for i in album)


class UnmatchedFiles(Cluster):
    """Special cluster for 'Unmatched Files' which have no PUID and have not been clustered."""

    can_remove = False
    can_edit_tags = False
    can_browser_lookup = False

    def __init__(self):
        super(UnmatchedFiles, self).__init__(_(u"Unmatched Files"))

    def add_new_files(self, files):
        self.files.extend(files)
        self.appendChildren(files)
        self.metadata.length += sum(f.metadata.length for f in files)
        self.update()
        self.tagger.window.enable_cluster(True)
        self.tagger.num_pending_files += len(files)

    def add_file(self, file):
        Cluster.add_file(self, file)
        self.tagger.window.enable_cluster(len(self) > 0)

    def remove_file(self, file):
        Cluster.remove_file(self, file)
        self.tagger.window.enable_cluster(len(self) > 0)

    def lookup_metadata(self):
        self.tagger.autotag(self.files)

    def remove(self):
        pass

    def column(self, column):
        if column == "~length":
            return ""
        return ClusterItem.column(self, column)

    @property
    def can_autotag(self):
        return len(self.files) > 0


class ClusterList(UserDict, TreeItem):

    can_browser_lookup = False

    def __init__(self):
        UserDict.__init__(self)
        TreeItem.__init__(self)

    def __hash__(self):
        return id(self)

    def __nonzero__(self):
        return True

    def iterfiles(self, save=False):
        for cluster in self.itervalues():
            for file in cluster.iterfiles():
                yield file

    def drop_files(self, files):
        self.tagger.cluster(files)

    def column(self, column):
        if column == "title":
            return _("Clusters")
        return ""

    @property
    def can_save(self):
        return len(self) > 0

    @property
    def can_analyze(self):
        return any(cluster.can_analyze for cluster in self.itervalues())

    @property
    def can_autotag(self):
        return len(self) > 0


class ClusterDict(object):

    def __init__(self):
        # word -> id index
        self.words = {}
        # id -> word, token index
        self.ids = {}
        # counter for new id generation
        self.id = 0
        self.regexp = re.compile(ur'\W', re.UNICODE)
        self.spaces = re.compile(ur'\s', re.UNICODE)

    def getSize(self):
        return self.id

    def tokenize(self, word):
        token = self.regexp.sub(u'', word.lower())
        return token if token else self.spaces.sub(u'', word.lower())

    def add(self, word):
        """
        Add a new entry to the cluster if it does not exist. If it
        does exist, increment the count. Return the index of the word
        in the dictionary or -1 is the word is empty.
        """

        if word == u'':
           return -1

        token = self.tokenize(word)
        if token == u'':
           return -1

        try:
           index, count = self.words[word]
           self.words[word] = (index, count + 1)
        except KeyError:
           index = self.id
           self.words[word] = (self.id, 1)
           self.ids[index] = (word, token)
           self.id = self.id + 1

        return index

    def getWord(self, index):
        word = None
        try:
            word, token = self.ids[index]
        except KeyError:
            pass
        return word

    def getToken(self, index):
        token = None;
        try:
            word, token = self.ids[index]
        except KeyError:
            pass
        return token

    def getWordAndCount(self, index):
        word = None
        count = 0
        try:
           word, token = self.ids[index]
           index, count = self.words[word]
        except KeyError:
           pass
        return word, count


class ClusterEngine(object):

    def __init__(self, clusterDict):
        # the cluster dictionary we're using
        self.clusterDict = clusterDict
        # keeps track of unique cluster index
        self.clusterCount = 0
        # Keeps track of the clusters we've created
        self.clusterBins = {}
        # Index the word ids -> clusters
        self.idClusterIndex = {}

    def getClusterFromId(self, id):
        return self.idClusterIndex.get(id)

    def printCluster(self, cluster):
        if cluster < 0:
            print "[no such cluster]"
            return

        bin = self.clusterBins[cluster]
        print cluster, " -> ", ", ".join([("'" + self.clusterDict.getWord(i) + "'") for i in bin])

    def getClusterTitle(self, cluster):

        if cluster < 0:
            return ""

        max = 0
        maxWord = u''
        for id in self.clusterBins[cluster]:
            word, count = self.clusterDict.getWordAndCount(id)
            if count >= max:
                maxWord = word
                max = count

        return maxWord

    def cluster(self, threshold):

        # Keep the matches sorted in a heap
        heap = []

        for y in xrange(self.clusterDict.getSize()):
            for x in xrange(y):
                if x != y:
                    c = similarity(self.clusterDict.getToken(x).lower(),
                                   self.clusterDict.getToken(y).lower())
                    #print "'%s' - '%s' = %f" % (
                    #    self.clusterDict.getToken(x).encode('utf-8', 'replace').lower(),
                    #    self.clusterDict.getToken(y).encode('utf-8', 'replace').lower(), c)

                    if c >= threshold:
                        heappush(heap, ((1.0 - c), [x, y]))
            QtCore.QCoreApplication.processEvents()

        for i in xrange(self.clusterDict.getSize()):
            word, count = self.clusterDict.getWordAndCount(i)
            if word and count > 1:
                self.clusterBins[self.clusterCount] = [ i ]
                self.idClusterIndex[i] = self.clusterCount
                self.clusterCount = self.clusterCount + 1
                #print "init ",
                #self.printCluster(self.clusterCount - 1)

        for i in xrange(len(heap)):
            c, pair = heappop(heap)
            c = 1.0 - c

            try:
                match0 = self.idClusterIndex[pair[0]]
            except:
                match0 = -1

            try:
                match1 = self.idClusterIndex[pair[1]]
            except:
                match1 = -1

            # if neither item is in a cluster, make a new cluster
            if match0 == -1 and match1 == -1:
                self.clusterBins[self.clusterCount] = [pair[0], pair[1]]
                self.idClusterIndex[pair[0]] = self.clusterCount
                self.idClusterIndex[pair[1]] = self.clusterCount
                self.clusterCount = self.clusterCount + 1
                #print "new ",
                #self.printCluster(self.clusterCount - 1)
                continue

            # If cluster0 is in a bin, stick the other match into that bin
            if match0 >= 0 and match1 < 0:
                self.clusterBins[match0].append(pair[1])
                self.idClusterIndex[pair[1]] = match0
                #print "add '%s' to cluster " % (self.clusterDict.getWord(pair[0])),
                #self.printCluster(match0)
                continue

            # If cluster1 is in a bin, stick the other match into that bin
            if match1 >= 0 and match0 < 0:
                self.clusterBins[match1].append(pair[0])
                self.idClusterIndex[pair[0]] = match1
                #print "add '%s' to cluster " % (self.clusterDict.getWord(pair[1])),
                #self.printCluster(match0)
                continue

            # If both matches are already in two different clusters, merge the clusters
            if match1 != match0:
                self.clusterBins[match0].extend(self.clusterBins[match1])
                for match in self.clusterBins[match1]:
                    self.idClusterIndex[match] = match0
                #print "col cluster %d into cluster" % (match1),
                #self.printCluster(match0)
                del self.clusterBins[match1]

        return self.clusterBins
