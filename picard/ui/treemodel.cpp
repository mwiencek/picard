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

#include <Qt>
#include <QtCore/QList>
#include <QtCore/QModelIndex>
#include <QtCore/QVariant>
#include "treemodel.h"


int TreeItem::row()
{
    if (parent == NULL)
        return 0;

    return parent->children->indexOf(this);
};

void TreeItem::update()
{
    if (model)
        emit model->dataChanged(model->indexOf(this),
             model->createIndex(row(), 2, this));
};

void TreeItem::appendChild(TreeItem *item)
{
    if (model) model->appendItem(item, this);
};

void TreeItem::appendChildren(QList<TreeItem *> *items)
{
    if (model) model->appendItems(items, this);
};

void TreeItem::removeChild(TreeItem *item)
{
    if (model) model->removeItem(item);
};

void TreeItem::replaceChildren(QList<TreeItem *> *newChildren)
{
    if (model) {
        model->clearChildren(this);
        model->appendItems(newChildren, this);
    }
};

void TreeItem::setExpanded(bool expanded)
{
    if (model) emit model->itemExpanded(index(), expanded);
};

void TreeItem::setHidden(bool hidden)
{
    if (model) emit model->itemHidden(index(), hidden);
};

int TreeItem::childCound() const
{
    return children->size();
};

QModelIndex TreeItem::index() const
{
    if (model)
        return model->indexOf(const_cast<TreeItem *>(this));

    return QModelIndex();
};


TreeModel::TreeModel()
{
    root = new TreeItem();
    root->model = this;
};

TreeModel::~TreeModel()
{
    delete root;
};

int TreeModel::columnCount(const QModelIndex &parent) const
{
    Q_UNUSED(parent);
    // needs to be changed if we ever support custom columns
    return 3;
};

TreeItem *TreeModel::itemFromIndex(const QModelIndex &index) const
{
    if (index.isValid())
        return (TreeItem *)index.internalPointer();

    return NULL;
};

int TreeModel::rowCount(const QModelIndex &parent) const
{
    if (parent.isValid()) {
        if (parent.column() > 0)
            return 0;

        return itemFromIndex(parent)->children->size();
    }
    return root->children->size();
};

QModelIndex TreeModel::index(int row, int column, const QModelIndex &parent) const
{
    TreeItem *par = itemFromIndex(parent);

    if (!par)
        par = root;

    if (row >= par->children->size())
        return QModelIndex();

    return createIndex(row, column, par->children->at(row));
};

QModelIndex TreeModel::parent(const QModelIndex &index) const
{
    TreeItem *item = itemFromIndex(index);

    if (!item || item == root)
        return QModelIndex();

    return indexOf(item->parent);
};

QModelIndex TreeModel::indexOf(TreeItem *item) const
{
    if (!item || item == root)
        return QModelIndex();

    return createIndex(item->row(), 0, item);
};

Qt::ItemFlags TreeModel::flags(const QModelIndex &index) const
{
    Q_UNUSED(index);

    return (Qt::ItemIsEnabled | Qt::ItemIsSelectable | Qt::ItemIsDragEnabled |
            Qt::ItemIsDropEnabled);
};

void TreeModel::appendItems(QList<TreeItem *> *items, TreeItem *parent)
{
    int count;
    if (!items || (count = items->size()) == 0)
        return;

    if (parent == NULL)
        parent = root;

    int row = parent->children->size();
    TreeItem *item;

    beginInsertRows(indexOf(parent), row, row + count - 1);

    for (int i = 0; i < count; i++) {
        item = items->at(i);

        if (item->parent)
            removeItem(item);

        item->parent = parent;
        item->model = this;
        parent->children->append(item);
    };

    endInsertRows();
};

void TreeModel::appendItem(TreeItem *item, TreeItem *parent)
{
    if (item->parent)
        removeItem(item);

    if (parent == NULL)
        parent = root;

    int row = parent->children->size();

    beginInsertRows(indexOf(parent), row, row);

    parent->children->append(item);
    item->parent = parent;
    item->model = this;

    endInsertRows();
};

void TreeModel::removeItem(TreeItem *item)
{
    clearChildren(item);

    int row = item->row();

    beginRemoveRows(indexOf(item->parent), row, row);

    item->parent->children->removeAt(row);
    item->parent = NULL;
    item->model = NULL;

    endRemoveRows();
};

void TreeModel::removeItems(QList<TreeItem *> *items)
{
    int count;
    if (!items || (count = items->size()) == 0)
        return;

    for (int i = 0; i < count; i++)
        removeItem(items->at(i));
};

void TreeModel::clearChildren(TreeItem *parent)
{
    int count = parent->children->size();
    if (!count) return;

    TreeItem *child;

    beginRemoveRows(indexOf(parent), 0, count - 1);

    for (int i = 0; i < count; i++) {
        child = parent->children->at(i);
        child->parent = NULL;
        child->model = NULL;
        clearChildren(child);
    };

    parent->children->clear();
    endRemoveRows();
};
