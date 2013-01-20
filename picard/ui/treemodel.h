/*
 * Picard, the next-generation MusicBrainz tagger
 * Copyright (C) 2013 Michael Wiencek
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 */

#ifndef _TREEMODEL_H_
#define _TREEMODEL_H_

#include <Qt>
#include <QtCore/QList>
#include <QtCore/QAbstractItemModel>
#include <QtCore/QModelIndex>
#include <QtCore/QVariant>
#include <Python.h>


class TreeModel;


class TreeItem
{
    private:
        TreeItem(const TreeItem &);

        int row();

        TreeItem *parent;
        TreeModel *model;

        QList<TreeItem *> *children;

    public:
        TreeItem() : parent(NULL),
                     model(NULL),
                     children(new QList<TreeItem *>()) {}

        ~TreeItem() { delete children; }

        virtual void update();

        void appendChild(TreeItem *item);
        void appendChildren(QList<TreeItem *> *items);
        void removeChild(TreeItem *item);
        void replaceChildren(QList<TreeItem *> *newChildren);

        void setExpanded(bool expanded);
        void setHidden(bool hidden);

        int childCound() const;
        QModelIndex index() const;
        TreeItem *parentItem() const { return parent; }

        // Return if this object can be saved.
        virtual const bool can_save() { return false; }
        // Return if this object can be removed.
        virtual const bool can_remove() { return false; }
        // Return if this object supports tag editing.
        virtual const bool can_edit_tags() { return false; }
        // Return if this object can be fingerprinted.
        virtual const bool can_analyze() { return false; }
        // Return if this object can be autotagged.
        virtual const bool can_autotag() { return false; }
        // Return if this object can be refreshed.
        virtual const bool can_refresh() { return false; }
        virtual const bool can_view_info() { return false; }
        virtual const bool can_browser_lookup() { return true; }
        virtual const bool is_album_like() { return false; }

        friend class TreeModel;
};


class TreeModel : public QAbstractItemModel
{
    Q_OBJECT

    private:
        TreeModel(const TreeModel &);

        TreeItem *root;

    public:
        TreeModel();
        ~TreeModel();

        int columnCount(const QModelIndex &parent) const;
        int rowCount(const QModelIndex &parent) const;
        QModelIndex index(int row, int column, const QModelIndex &parent) const;
        QModelIndex parent(const QModelIndex &index) const;
        Qt::ItemFlags flags(const QModelIndex &index) const;

        TreeItem *itemFromIndex(const QModelIndex &index) const;

        QModelIndex indexOf(TreeItem *item) const;

        void appendItems(QList<TreeItem *> *items, TreeItem *parent);
        void appendItem(TreeItem *item, TreeItem *parent);
        void removeItem(TreeItem *item);
        void removeItems(QList<TreeItem *> *items);
        void clearChildren(TreeItem *parent);

        friend class TreeItem;

    signals:
        void itemExpanded(const QModelIndex &index, bool expanded);
        void itemHidden(const QModelIndex &index, bool hidden);
};

#endif
