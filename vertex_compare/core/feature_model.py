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
    List
)

from qgis.PyQt.QtCore import (
    Qt,
    QAbstractItemModel,
    QObject,
    QModelIndex
)
from qgis.core import (
    QgsFeature,
    QgsVertexId,
    QgsPoint,
    QgsVectorLayer,
    QgsFeatureRequest,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextUtils
)


class FeatureModel(QAbstractItemModel):
    """
    A model for showing features
    """

    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.layer: Optional[QgsVectorLayer] = None
        self.fids: List[int] = []
        self.features: List[QgsFeature] = []
        self.display_expressions = []

    def set_feature_ids(self, layer: Optional[QgsVectorLayer], fids: List[int]):
        """
        Sets the feature ids to show in the model
        """
        self.beginRemoveRows(QModelIndex(), 0, len(self.features)-1 )
        self.features = []
        self.display_expressions = []
        self.endRemoveRows()

        if layer is None:
            self.fids = []
            return

        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))

        display_expression = QgsExpression(layer.displayExpression())
        display_expression.prepare(context)

        request = QgsFeatureRequest().setFilterFids(fids)
        request.setSubsetOfAttributes(display_expression.referencedColumns(), layer.fields())

        pending_features = [f for f in layer.getFeatures(request)]

        self.beginInsertRows(QModelIndex(), 0, len(pending_features))
        self.features = pending_features
        self.fids = fids
        for f in self.features:
            context.setFeature(f)
            self.display_expressions.append(display_expression.evaluate(context))

        self.endInsertRows()

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()):
        return self.createIndex(row, column, None)

    def parent(self, child: QModelIndex) -> QModelIndex:
        return QModelIndex()

    def rowCount(self,  # pylint: disable=missing-function-docstring
                 parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0

        return len(self.features)

    def columnCount(self,  # pylint: disable=missing-function-docstring
                    parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return 1

    def data(self,  # pylint: disable=missing-function-docstring, too-many-return-statements
             index: QModelIndex,
             role: int = Qt.DisplayRole):
        if index.row() < 0 or index.row() >= len(self.features):
            return None

        if role in (Qt.DisplayRole, Qt.ToolTipRole, Qt.EditRole):
            return f'{self.features[index.row()].id()}: {self.display_expressions[index.row()]}'

        return None