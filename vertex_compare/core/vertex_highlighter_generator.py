# -*- coding: utf-8 -*-
"""Vertex highlighter renderer generator

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

from qgis.PyQt.QtCore import (
    Qt
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
    QgsMarkerLineSymbolLayer,
    QgsMarkerSymbol,
    QgsSymbolLayer,
    QgsProperty,
    QgsSimpleMarkerSymbolLayer,
    QgsTextFormat,
    QgsNullSymbolRenderer
)

from vertex_compare.core.settings_registry import SettingsRegistry
from vertex_compare.core.text_renderer_marker_symbol_layer import TextRendererMarkerSymbolLayer
from vertex_compare.core.vertex_highlighter_renderer import VertexHighlighterRenderer


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
        if SettingsRegistry.label_filtering() == SettingsRegistry.LABEL_NONE:
            return QgsNullSymbolRenderer()

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
