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

from typing import Optional, Dict, List

from qgis.PyQt.QtGui import (
    QColor
)
from qgis.core import (
    QgsSingleSymbolRenderer,
    QgsFields,
    QgsRenderContext,
    QgsMarkerLineSymbolLayer,
    QgsMarkerSymbol,
    QgsSymbolLayer,
    QgsProperty,
    QgsWkbTypes,
    QgsLineSymbol,
    QgsFillSymbol,
    QgsGeometry,
    QgsPointXY,
    QgsVertexId,
    QgsFeatureSource,
    QgsFeatureRequest
)

from vertex_compare.core.settings_registry import SettingsRegistry
from vertex_compare.core.text_renderer_marker_symbol_layer import TextRendererMarkerSymbolLayer


class VertexHighlighterRenderer(QgsSingleSymbolRenderer):
    """
    Custom layer renderer which highlights vertices in selected features only
    """

    COLORS = [
        QColor(255, 0, 0),
        QColor(0, 150, 0),
        QColor(0, 0, 255),
    ]

    def __init__(self,
                 source: QgsFeatureSource,
                 layer_type: QgsWkbTypes.GeometryType,
                 selection: list,
                 vertex_number=Optional[int],
                 topological_geometries: Optional[Dict[int, QgsGeometry]] = None):
        if layer_type == QgsWkbTypes.LineGeometry:
            symbol = QgsLineSymbol()
        else:
            symbol = QgsFillSymbol()

        marker_line = QgsMarkerLineSymbolLayer()
        marker_line.setRotateMarker(False)
        marker_line.setPlacement(QgsMarkerLineSymbolLayer.Vertex)

        vertex_marker_symbol = SettingsRegistry.vertex_symbol()
        # not so nice, but required to allow us to dynamically change this color mid-way through rendering
        for layer in vertex_marker_symbol:
            layer.setDataDefinedProperty(QgsSymbolLayer.PropertyFillColor, QgsProperty.fromValue(None))

        font_marker_symbol = QgsMarkerSymbol()

        text_format = SettingsRegistry.vertex_format()
        font_marker = TextRendererMarkerSymbolLayer(text_format, vertex_number)
        font_marker.setSubSymbol(vertex_marker_symbol)

        font_marker_symbol.changeSymbolLayer(0, font_marker)
        marker_line.setSubSymbol(font_marker_symbol)

        symbol.changeSymbolLayer(0, marker_line)

        symbol.setClipFeaturesToExtent(False)

        super().__init__(symbol)

        self.selection = sorted(selection)
        self.feature_index = 0
        self.vertex_number = vertex_number
        self.source = source

        self.topological_geometries = topological_geometries

    def calculate_topology(self) -> Dict[int, List[int]]:
        """
        Calculates the topological relationship between vertices
        """
        f1, f2 = self.topological_geometries.keys()
        g1 = self.topological_geometries[f1]
        g2 = self.topological_geometries[f2]

        g1_points = set(v.asPoint() for v in g1.coerceToType(QgsWkbTypes.Point))
        g2_points = set(v.asPoint() for v in g2.coerceToType(QgsWkbTypes.Point))

        common_vertices = g1_points.intersection(g2_points)

        def _get_uncommon_vertices(_common_vertices, geometry: QgsGeometry):
            res = []

            const_geom = geometry.constGet()
            vid = QgsVertexId()

            vertex_no = 1
            while True:
                ok, vertex = const_geom.nextVertex(vid)
                if ok:
                    if not QgsPointXY(vertex) in _common_vertices:
                        res.append(vertex_no)
                    vertex_no += 1
                else:
                    break

            return res

        return {f1: _get_uncommon_vertices(common_vertices, g1),
                f2: _get_uncommon_vertices(common_vertices, g2)}

    def filter(self, _=QgsFields()) -> str:  # pylint: disable=missing-function-docstring
        return f'$id in ({",".join([str(i) for i in self.selection])})'

    def startRender(self, context: QgsRenderContext, fields: QgsFields):  # pylint: disable=missing-function-docstring
        # we are in a background thread now - we can do more costly things!

        # we need a record of the number of vertices in each geometry part
        selected_features = self.source.getFeatures(QgsFeatureRequest().setFilterFids(self.selection).setNoAttributes())
        geometry_part_map = {}
        for f in selected_features:
            if f.geometry().isMultipart():
                geometry_part_map[f.id()] = []
                for part in f.geometry().constParts():
                    geometry_part_map[f.id()].append(part.nCoordinates())

        self.symbol()[0].subSymbol()[0].set_geometry_part_map(geometry_part_map)
        self.feature_index = 0

        if self.topological_geometries:
            self.symbol()[0].subSymbol()[0].set_uncommon_vertices(self.calculate_topology())

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
