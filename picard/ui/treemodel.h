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

        bool hidden;

    public:
        TreeItem() : parent(NULL),
                     model(NULL),
                     children(new QList<TreeItem *>()),
                     hidden(false) {}

        ~TreeItem() { delete children; }

        virtual void update();

        void appendChild(TreeItem *item);
        void appendChildren(QList<TreeItem *> *items);
        void removeChild(TreeItem *item);
        void replaceChildren(QList<TreeItem *> *newChildren);
        void sortChildren(int column, Qt::SortOrder order);

        int childCound() const;
        TreeItem *parentItem() const { return parent; }

        // Return if this object can be saved.
        static const bool can_save = false;
        // Return if this object can be removed.
        static const bool can_remove = false;
        // Return if this object supports tag editing.
        static const bool can_edit_tags = false;
        // Return if this object can be fingerprinted.
        static const bool can_analyze = false;
        // Return if this object can be autotagged.
        static const bool can_autotag = false;
        // Return if this object can be refreshed.
        static const bool can_refresh = false;
        static const bool can_view_info = false;
        static const bool can_browser_lookup = true;

        static const char PENDING = 0;
        static const char NORMAL = 1;
        static const char CHANGED = 2;
        static const char ERROR = 3;
        static const char REMOVED = 4;

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

        virtual bool sortComparator(int column, Qt::SortOrder order, TreeItem *a, TreeItem *b) const;
        TreeItem *itemFromIndex(const QModelIndex &index) const;
        QModelIndex indexOf(TreeItem *item) const;

        void appendItems(QList<TreeItem *> *items, TreeItem *parent);
        void appendItem(TreeItem *item, TreeItem *parent);
        void removeItem(TreeItem *item);
        void clearChildren(TreeItem *parent);
        virtual void sort(int column, Qt::SortOrder order);

        friend class TreeItem;
};


class SortFunction {
    private:
        const TreeModel *model;
        const int column;
        const Qt::SortOrder order;

    public:
        SortFunction(TreeModel *model, int column, Qt::SortOrder order)
            : model(model), column(column), order(order) {};

        bool operator()(TreeItem *a, TreeItem *b) {
            return model->sortComparator(column, order, a, b);
        };
};

#endif
