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

from typing import Optional

from qgis.core import (
    QgsFeatureRendererGenerator,
    QgsSingleSymbolRenderer,
    QgsVectorLayer,
    QgsNullSymbolRenderer
)

from vertex_compare.core.settings_registry import SettingsRegistry
from vertex_compare.core.vertex_highlighter_renderer import VertexHighlighterRenderer


class VertexHighlighterRendererGenerator(QgsFeatureRendererGenerator):
    """
    Generates a vertex highlighter renderer for layers
    """

    ID = 'vertex_highlighter'

    def __init__(self, layer: QgsVectorLayer, feature_id: Optional[int], vertex_number: Optional[int]):
        """
        Creates a vertex highlighter for the specified layer type

        Optional a selected feature_id and vertex_number can be specified.
        """
        super().__init__()
        self.layer = layer
        self.layer_type = layer.geometryType()
        self.feature_id = feature_id
        self.vertex_number = vertex_number

    def id(self):  # pylint: disable=missing-function-docstring
        return VertexHighlighterRendererGenerator.ID

    def level(self) -> float:  # pylint: disable=missing-function-docstring
        return 1

    def createRenderer(self) -> QgsSingleSymbolRenderer:  # pylint: disable=missing-function-docstring
        filtering = SettingsRegistry.label_filtering()

        if filtering == SettingsRegistry.LABEL_NONE:
            return QgsNullSymbolRenderer()
        if filtering == SettingsRegistry.LABEL_SELECTED:
            if self.feature_id is None or self.vertex_number is None:
                # labeling selected vertex only, and no selection => no renderer
                return QgsNullSymbolRenderer()
            selection = {self.feature_id}
        else:
            selection = self.layer.selectedFeatureIds()

        return VertexHighlighterRenderer(self.layer_type, selection, self.vertex_number)
