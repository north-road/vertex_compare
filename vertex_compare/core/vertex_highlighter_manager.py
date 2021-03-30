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
    QgsVectorLayer
)

from vertex_compare.core.vertex_highlighter_generator import VertexHighlighterRendererGenerator


class VertexHighlighterManager:
    """
    Manages highlighting of vertices for one single active layer only
    """

    def __init__(self):
        super().__init__()

        self.layer: Optional[QgsVectorLayer] = None
        self.visible = False

    def __del__(self):
        if self.layer is not None:
            self.layer.removeFeatureRendererGenerator(VertexHighlighterRendererGenerator.ID)
            self.layer.triggerRepaint()

    def set_layer(self, layer: QgsVectorLayer):
        """
        Sets the active layer
        """
        if self.layer is not None:
            # this is safe to call even if a generator isn't installed!
            self.layer.removeFeatureRendererGenerator(VertexHighlighterRendererGenerator.ID)
            self.layer.triggerRepaint()

        self.layer = layer
        if self.layer is not None and self.visible:
            self.layer.addFeatureRendererGenerator(VertexHighlighterRendererGenerator(self.layer))
            self.layer.triggerRepaint()

    def set_visible(self, visible: bool):
        """
        Sets whether the vertex highlights should be visible
        """
        self.visible = visible
        if not self.visible and self.layer is not None:
            # this is safe to call even if a generator isn't installed!
            self.layer.removeFeatureRendererGenerator(VertexHighlighterRendererGenerator.ID)
            self.layer.triggerRepaint()
        elif self.visible and self.layer is not None:
            self.layer.addFeatureRendererGenerator(VertexHighlighterRendererGenerator(self.layer))
            self.layer.triggerRepaint()

