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

from qgis.core import (
    QgsFeatureRendererGenerator,
    QgsSingleSymbolRenderer,
    QgsLineSymbol,
    QgsVectorLayer,
    QgsWkbTypes,
    QgsFillSymbol,
    QgsSymbol,
    QgsFields
)


class VertexHighlighterRenderer(QgsSingleSymbolRenderer):
    """
    Custom layer renderer which highlights vertices in selected features only
    """

    def __init__(self, symbol: QgsSymbol, selection: list):
        super().__init__(symbol)
        self.selection = selection

    def filter(self, _=QgsFields()) -> str:  # pylint: disable=missing-function-docstring
        return f'$id in ({",".join([str(i) for i in self.selection])})'

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
        if self.layer_type == QgsWkbTypes.LineGeometry:
            symbol = QgsLineSymbol.createSimple({'color': '#ffffff'})
        else:
            symbol = QgsFillSymbol.createSimple({'color': '#ffffff'})
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
