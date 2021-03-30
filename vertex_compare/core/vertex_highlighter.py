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

from typing import Optional

from qgis.PyQt.QtCore import (
    QPointF,
    Qt,
    QRectF
)
from qgis.PyQt.QtGui import (
    QColor
)
from qgis.core import (
    QgsFeatureRendererGenerator,
    QgsSingleSymbolRenderer,
    QgsLineSymbol,
    QgsVectorLayer,
    QgsWkbTypes,
    QgsFillSymbol,
    QgsSymbol,
    QgsFields,
    QgsMarkerLineSymbolLayer,
    QgsMarkerSymbol,
    QgsSymbolLayer,
    QgsProperty,
    QgsMarkerSymbolLayer,
    QgsSimpleMarkerSymbolLayer,
    QgsSymbolRenderContext,
    QgsTextFormat,
    QgsTextRenderer,
    QgsRenderContext,
    QgsFeature,
    QgsUnitTypes
)


class TextRendererMarkerSymbolLayer(QgsMarkerSymbolLayer):
    """
    A marker symbol layer which uses QgsTextRenderer to draw text
    """

    def __init__(self, text_format: QgsTextFormat):
        super().__init__()
        self.text_format = text_format
        self.vertex_id = 1

    def layerType(self) -> str:  # pylint: disable=missing-function-docstring
        return 'TextRenderer'

    def startRender(self, context: QgsSymbolRenderContext):  # pylint: disable=missing-function-docstring,unused-argument
        self.vertex_id = 1

    def stopRender(self, context: QgsSymbolRenderContext):  # pylint: disable=missing-function-docstring,unused-argument
        self.vertex_id = 1

    def usedAttributes(self, context: QgsRenderContext):  # pylint: disable=missing-function-docstring
        return self.text_format.referencedFields(context)

    def setColor(self, color):  # pylint: disable=missing-function-docstring
        self.text_format.setColor(color)

    def startFeatureRender(self, feature: QgsFeature, context: QgsRenderContext):  # pylint: disable=missing-function-docstring
        self.vertex_id = 1
        super().startFeatureRender(feature, context)

    def renderPoint(self, point: QPointF, context: QgsSymbolRenderContext):  # pylint: disable=missing-function-docstring
        if not context.renderContext().painter():
            return

        # offset point a little
        offset = context.renderContext().convertToPainterUnits(1, QgsUnitTypes.RenderMillimeters)
        render_point = QPointF(point.x() + offset, point.y() - offset)

        QgsTextRenderer.drawText(render_point, 0, QgsTextRenderer.AlignLeft,
                                 [str(self.vertex_id)], context.renderContext(), self.text_format)
        self.vertex_id += 1

    def clone(self):  # pylint: disable=missing-function-docstring
        return TextRendererMarkerSymbolLayer(self.text_format)

    def properties(self):  # pylint: disable=missing-function-docstring
        return {}

    def bounds(self, point: QPointF, context: QgsSymbolRenderContext):  # pylint: disable=missing-function-docstring,unused-argument
        return QRectF()


class VertexHighlighterRenderer(QgsSingleSymbolRenderer):
    """
    Custom layer renderer which highlights vertices in selected features only
    """

    COLORS = [
        QColor(255, 0, 0),
        QColor(0, 150, 0),
        QColor(0, 0, 255),
    ]

    def __init__(self, symbol: QgsSymbol, selection: list):
        super().__init__(symbol)
        self.selection = sorted(selection)
        self.feature_index = 0

    def filter(self, _=QgsFields()) -> str:  # pylint: disable=missing-function-docstring
        return f'$id in ({",".join([str(i) for i in self.selection])})'

    def startRender(self, context: QgsRenderContext, fields: QgsFields):  # pylint: disable=missing-function-docstring
        self.feature_index = 0
        super().startRender(context, fields)

    def renderFeature(self,  # pylint: disable=missing-function-docstring
                      feature,
                      context,
                      layer,
                      _,
                      drawVertexMarker) -> bool:
        # we ignore whatever passed value is given for the "selected" argument. In fact, it's always
        # False for secondary renderers, but even if it wasn't we still don't want to pass it on
        # to the base class renderFeature method
        if not context.showSelection():
            return False

        if feature.id() not in self.selection:
            return False

        color = VertexHighlighterRenderer.COLORS[self.feature_index % len(VertexHighlighterRenderer.COLORS)]
        self.feature_index += 1

        self.symbol().setColor(color)

        return super().renderFeature(feature, context, layer, False, drawVertexMarker)


class VertexHighlighterRendererGenerator(QgsFeatureRendererGenerator):
    """
    Generates a vertex highlighter renderer for layers
    """

    ID = 'vertex_highlighter'

    def __init__(self, layer: QgsVectorLayer):
        """
        Creates a vertex highlighter for the specified layer type
        """
        super().__init__()
        self.layer = layer
        self.layer_type = layer.geometryType()

    def id(self):  # pylint: disable=missing-function-docstring
        return VertexHighlighterRendererGenerator.ID

    def level(self) -> float:  # pylint: disable=missing-function-docstring
        return 1

    def createRenderer(self) -> QgsSingleSymbolRenderer:  # pylint: disable=missing-function-docstring
        selection = self.layer.selectedFeatureIds()

        marker_line = QgsMarkerLineSymbolLayer()
        marker_line.setRotateMarker(False)
        marker_line.setPlacement(QgsMarkerLineSymbolLayer.Vertex)

        vertex_marker_symbol = QgsMarkerSymbol()

        simple_marker = QgsSimpleMarkerSymbolLayer(QgsSimpleMarkerSymbolLayer.Circle)
        simple_marker.setSize(1)
        simple_marker.setStrokeStyle(Qt.NoPen)
        # not so nice, but required to allow us to dynamically change this color mid-way through rendering
        simple_marker.setDataDefinedProperty(QgsSymbolLayer.PropertyFillColor, QgsProperty.fromValue(None))
        vertex_marker_symbol.changeSymbolLayer(0, simple_marker)

        text_format = QgsTextFormat()
        text_format.setColor(QColor(255, 0, 0))
        text_format.setSize(10)
        text_format.setNamedStyle('Bold')
        text_format.buffer().setEnabled(True)
        text_format.buffer().setColor(QColor(255, 255, 255))

        font_marker = TextRendererMarkerSymbolLayer(text_format)
        vertex_marker_symbol.appendSymbolLayer(font_marker)

        marker_line.setSubSymbol(vertex_marker_symbol)

        if self.layer_type == QgsWkbTypes.LineGeometry:
            symbol = QgsLineSymbol()
        else:
            symbol = QgsFillSymbol()

        symbol.changeSymbolLayer(0, marker_line)

        symbol.setClipFeaturesToExtent(False)

        return VertexHighlighterRenderer(symbol, selection)


class VertexHighlighterManager:
    """
    Manages highlighting of vertices for one single active layer only
    """

    def __init__(self):
        super().__init__()

        self.layer: Optional[QgsVectorLayer] = None

    def __del__(self):
        if self.layer is not None:
            self.layer.removeFeatureRendererGenerator(VertexHighlighterRendererGenerator.ID)
            self.layer.triggerRepaint()

    def set_layer(self, layer: QgsVectorLayer):
        """
        Sets the active layer
        """
        if self.layer == layer:
            return

        if self.layer is not None:
            # this is safe to call even if a generator isn't installed!
            self.layer.removeFeatureRendererGenerator(VertexHighlighterRendererGenerator.ID)
            self.layer.triggerRepaint()

        self.layer = layer
        if self.layer is not None:
            self.layer.addFeatureRendererGenerator(VertexHighlighterRendererGenerator(self.layer))
            self.layer.triggerRepaint()
