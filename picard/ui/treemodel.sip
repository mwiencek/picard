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

%Module treemodel

%Import QtCore/QtCoremod.sip

%ModuleCode
TreeItem *pyobject_to_treeitem(PyObject *obj, int *err) {
    return (TreeItem *)sipConvertToType(obj, sipType_TreeItem, NULL, NULL, NULL, err);
}

QList<TreeItem *> *pylist_to_qlist(PyObject *list, int *err) {
    Py_ssize_t count;

    if (!PyList_Check(list) || (count = PyList_GET_SIZE(list)) == 0)
        return NULL;

    QList<TreeItem *> *items = new QList<TreeItem *>();
    PyObject *obj;

    for (int i = 0; i < count; i++) {
        obj = PyList_GET_ITEM(list, i);
        items->append(pyobject_to_treeitem(obj, err));
    };

    return items;
}
%End

%ModuleHeaderCode
#include "treemodel.h"

TreeItem *pyobject_to_treeitem(PyObject *obj, int *err);
QList<TreeItem *> *pylist_to_qlist(PyObject *list, int *err);
%End

class TreeItem
{
    private:
        TreeItem(const TreeItem &);

    public:
        TreeItem();
        ~TreeItem();

        virtual void update();

        void appendChild(SIP_PYOBJECT item);
        %MethodCode
            TreeItem *a0_item = pyobject_to_treeitem(a0, &sipIsErr);

            if (!sipIsErr)
                sipCpp->appendChild(a0_item);
        %End

        void appendChildren(SIP_PYLIST items);
        %MethodCode
            QList<TreeItem *> *a0_items = pylist_to_qlist(a0, &sipIsErr);

            if (!sipIsErr)
                sipCpp->appendChildren(a0_items);

            if (a0_items) delete a0_items;
        %End

        void removeChild(SIP_PYOBJECT item);
        %MethodCode
            TreeItem *a0_item = pyobject_to_treeitem(a0, &sipIsErr);

            if (!sipIsErr)
                sipCpp->removeChild(a0_item);
        %End

        void replaceChildren(SIP_PYLIST newChildren);
        %MethodCode
            QList<TreeItem *> *a0_items = pylist_to_qlist(a0, &sipIsErr);

            if (!sipIsErr)
                sipCpp->replaceChildren(a0_items);

            if (a0_items) delete a0_items;
        %End

        void setExpanded(bool expanded);
        void setHidden(bool hidden);

        int childCound() const;
        TreeItem *parentItem() const;

        static const bool can_save;
        static const bool can_remove;
        static const bool can_edit_tags;
        static const bool can_analyze;
        static const bool can_autotag;
        static const bool can_refresh;
        static const bool can_view_info;
        static const bool can_browser_lookup;
};


class TreeModel : public QAbstractItemModel
{
    private:
        TreeModel(const TreeModel &);

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

        void appendItems(SIP_PYLIST items, SIP_PYOBJECT parent);
        %MethodCode
            QList<TreeItem *> *a0_items = pylist_to_qlist(a0, &sipIsErr);

            if (!sipIsErr) {
                TreeItem *a1_item = pyobject_to_treeitem(a1, &sipIsErr);

                if (!sipIsErr)
                    sipCpp->appendItems(a0_items, a1_item);
            }
            if (a0_items) delete a0_items;
        %End

        void appendItem(SIP_PYOBJECT item, SIP_PYOBJECT parent);
        %MethodCode
            TreeItem *a0_item = pyobject_to_treeitem(a0, &sipIsErr);
            TreeItem *a1_item = pyobject_to_treeitem(a1, &sipIsErr);

            if (!sipIsErr)
                sipCpp->appendItem(a0_item, a1_item);
        %End

        void removeItem(SIP_PYOBJECT item);
        %MethodCode
            TreeItem *a0_item = pyobject_to_treeitem(a0, &sipIsErr);

            if (!sipIsErr)
                sipCpp->removeItem(a0_item);
        %End

    signals:
        void itemExpanded(const QModelIndex &index, bool expanded);
        void itemHidden(const QModelIndex &index, bool hidden);
};
