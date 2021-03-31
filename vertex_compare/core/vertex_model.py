# -*- coding: utf-8 -*-
"""Vertex highlighter renderer

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = '(C) 2021 by Nyall Dawson'
__date__ = '22/02/2021'
__copyright__ = 'Copyright 2021, North Road'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from typing import (
    Optional,
    List,
    Union
)

from qgis.PyQt.QtCore import (
    Qt,
    QAbstractTableModel,
    QObject,
    QModelIndex
)
from qgis.core import (
    QgsFeature,
    QgsVertexId,
    QgsPoint
)


class VertexModel(QAbstractTableModel):
    """
    A model for showing vertex information
    """

    VERTEX_NUMBER_ROLE = Qt.UserRole + 1

    COLUMN_ID = 0
    COLUMN_X = 1
    COLUMN_Y = 2
    COLUMN_Z = 3
    COLUMN_M = 4

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.feature: Optional[QgsFeature] = None
        self.vertices: List[Union[QgsVertexId, QgsPoint]] = []
        self.has_z = False
        self.has_m = False

    def set_feature(self, feature: Optional[QgsFeature]):
        """
        Sets the feature to show in the model
        """
        self.beginResetModel()
        self.feature = feature

        self.vertices = []

        self.has_z = self.feature.geometry().constGet().is3D() if self.feature is not None and self.feature.hasGeometry() else True
        self.has_m = self.feature.geometry().constGet().isMeasure() if self.feature is not None and self.feature.hasGeometry() else True

        if self.feature is not None and self.feature.hasGeometry():
            geom = self.feature.geometry().constGet()

            vid = QgsVertexId()
            while True:
                ok, vertex = geom.nextVertex(vid)
                if ok:
                    self.vertices.append((vid, vertex))
                else:
                    break

        self.endResetModel()

    def rowCount(self,  # pylint: disable=missing-function-docstring
                 parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0

        if self.feature is None:
            return 0

        return len(self.vertices)

    def columnCount(self,  # pylint: disable=missing-function-docstring
                    parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return 3 + (1 if self.has_z else 0) + (1 if self.has_m else 0)

    def data(self,  # pylint: disable=missing-function-docstring, too-many-return-statements
             index: QModelIndex,
             role: int = Qt.DisplayRole):
        if index.row() < 0 or index.row() >= len(self.vertices):
            return None

        if role in (Qt.DisplayRole, Qt.ToolTipRole, Qt.EditRole):
            if index.column() == VertexModel.COLUMN_ID:
                return index.row() + 1
            if index.column() == VertexModel.COLUMN_X:
                return "{:.2f}".format(self.vertices[index.row()][1].x())
            if index.column() == VertexModel.COLUMN_Y:
                return "{:.2f}".format(self.vertices[index.row()][1].y())
            if index.column() == VertexModel.COLUMN_Y + 1 and self.has_z:
                return "{:.2f}".format(self.vertices[index.row()][1].z())

            return "{:.2f}".format(self.vertices[index.row()][1].m())

        if role == VertexModel.VERTEX_NUMBER_ROLE:
            return index.row() + 1

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if orientation == Qt.Horizontal:
            if role in (Qt.DisplayRole, Qt.ToolTipRole):
                if section == VertexModel.COLUMN_ID:
                    return self.tr('Vertex')
                if section == VertexModel.COLUMN_X:
                    return self.tr('X')
                if section == VertexModel.COLUMN_Y:
                    return self.tr('Y')
                if section == VertexModel.COLUMN_Y + 1 and self.has_z:
                    return self.tr('Z')

                return self.tr('M')
        return None
