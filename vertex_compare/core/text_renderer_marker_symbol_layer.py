# -*- coding: utf-8 -*-
"""A QgsTextRenderer based marker symbol layer

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

from typing import Optional, Dict

from qgis.PyQt.QtCore import (
    QPointF,
    QRectF
)
from qgis.core import (
    QgsMarkerSymbolLayer,
    QgsSymbolRenderContext,
    QgsTextFormat,
    QgsTextRenderer,
    QgsRenderContext,
    QgsUnitTypes
)


class TextRendererMarkerSymbolLayer(QgsMarkerSymbolLayer):
    """
    A marker symbol layer which uses QgsTextRenderer to draw text
    """

    def __init__(self, text_format: QgsTextFormat, target_vertex: Optional[int]):
        super().__init__()
        self.text_format = text_format
        self.vertex_id = 1
        self.current_feature_id = None
        self.target_vertex = target_vertex
        self.marker_symbol = None
        self.uncommon_vertices = {}

    def layerType(self) -> str:  # pylint: disable=missing-function-docstring
        return 'TextRenderer'

    def set_uncommon_vertices(self, vertices: Dict):
        """
        Sets the dictionary of uncommon vertices between two selected geometries
        """
        self.uncommon_vertices = vertices

    def setSubSymbol(self, symbol):  # pylint: disable=missing-function-docstring
        self.marker_symbol = symbol
        return True

    def subSymbol(self):  # pylint: disable=missing-function-docstring
        return self.marker_symbol

    def startRender(self,  # pylint: disable=missing-function-docstring
                    context: QgsSymbolRenderContext):  # pylint: disable=unused-argument
        self.vertex_id = 1
        self.current_feature_id = None
        if self.subSymbol():
            self.subSymbol().startRender(context.renderContext(), context.fields())

    def stopRender(self, context: QgsSymbolRenderContext):  # pylint: disable=missing-function-docstring,unused-argument
        self.vertex_id = 1
        self.current_feature_id = None
        if self.subSymbol():
            self.subSymbol().stopRender(context.renderContext())

    def usedAttributes(self, context: QgsRenderContext):  # pylint: disable=missing-function-docstring
        return self.text_format.referencedFields(context)

    def setColor(self, color):  # pylint: disable=missing-function-docstring
        self.text_format.setColor(color)
        if self.subSymbol():
            self.subSymbol().setColor(color)

    def renderPoint(self,  # pylint: disable=missing-function-docstring
                    point: QPointF,
                    context: QgsSymbolRenderContext):
        if not context.renderContext().painter():
            return

        feature_id = context.feature().id()
        if feature_id != self.current_feature_id:
            self.current_feature_id = feature_id
            self.vertex_id = 1

        if feature_id in self.uncommon_vertices and self.vertex_id not in self.uncommon_vertices[feature_id]:
            self.vertex_id += 1
            return

        if self.target_vertex is not None and self.target_vertex != self.vertex_id:
            self.vertex_id += 1
            return

        map_point = context.renderContext().mapToPixel().toMapPoint(point.x(), point.y())
        if not context.renderContext().mapExtent().contains(map_point):
            # don't render points out of view
            self.vertex_id += 1
            return

        if self.subSymbol():
            self.subSymbol().renderPoint(point, None, context.renderContext())

        # offset point a little
        offset = context.renderContext().convertToPainterUnits(1, QgsUnitTypes.RenderMillimeters)
        render_point = QPointF(point.x() + offset, point.y() - offset)

        QgsTextRenderer.drawText(render_point, 0, QgsTextRenderer.AlignLeft,
                                 [str(self.vertex_id)], context.renderContext(), self.text_format)
        self.vertex_id += 1

    def clone(self):  # pylint: disable=missing-function-docstring
        res = TextRendererMarkerSymbolLayer(self.text_format, self.target_vertex)
        if self.subSymbol():
            res.setSubSymbol(self.subSymbol().clone())
        return res

    def properties(self):  # pylint: disable=missing-function-docstring
        return {}

    def bounds(self,  # pylint: disable=missing-function-docstring
               point: QPointF,  # pylint: disable=unused-argument
               context: QgsSymbolRenderContext):  # pylint: disable=unused-argument
        return QRectF()
