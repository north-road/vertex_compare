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

from qgis.PyQt import sip
from qgis.core import (
    QgsVectorLayer
)

from vertex_compare.core.settings_registry import SettingsRegistry
from vertex_compare.core.vertex_highlighter_generator import VertexHighlighterRendererGenerator


class VertexHighlighterManager:
    """
    Manages highlighting of vertices for one single active layer only
    """

    def __init__(self):
        super().__init__()

        self.layer: Optional[QgsVectorLayer] = None
        self.visible = False
        self.current_feature_id: Optional[int] = None
        self.current_vertex_number: Optional[int] = None

    def __del__(self):
        self._remove_current_generator()

    def set_layer(self, layer: QgsVectorLayer):
        """
        Sets the active layer
        """
        if layer == self.layer:
            return

        self._remove_current_generator()
        self.layer = layer
        self._reset_generator()

    def set_visible(self, visible: bool):
        """
        Sets whether the vertex highlights should be visible
        """
        if self.visible == visible:
            return

        self.visible = visible
        self._reset_generator()

    def redraw(self):
        """
        Forces a redraw of the current layer being highlighted
        """
        self._remove_current_generator()
        self._reset_generator()

    def set_selected_vertex(self, feature_id: Optional[int], vertex_number: Optional[int]):
        """
        Triggered when the selected vertex is changed
        """
        if self.current_vertex_number == vertex_number and self.current_feature_id == feature_id:
            return

        needs_redraw = SettingsRegistry.label_filtering() == SettingsRegistry.LABEL_SELECTED or \
                       (SettingsRegistry.label_filtering() == SettingsRegistry.LABEL_ALL and feature_id != self.current_feature_id)

        self.current_feature_id = feature_id
        self.current_vertex_number = vertex_number
        self._remove_current_generator()
        self._reset_generator(not needs_redraw)

    def _remove_current_generator(self):
        """
        Removes the generator from the current layer, if present
        """
        if self.layer is not None and not sip.isdeleted(self.layer):
            self.layer.removeFeatureRendererGenerator(VertexHighlighterRendererGenerator.ID)
            self.layer.triggerRepaint()

    def _reset_generator(self, skip_redraw: bool = False):
        """
        Creates a new renderer generator for the correct layer
        """
        if not self.visible:
            self._remove_current_generator()
        elif self.layer is not None:
            self.layer.addFeatureRendererGenerator(
                VertexHighlighterRendererGenerator(self.layer,
                                                   self.current_feature_id,
                                                   self.current_vertex_number))
            if not skip_redraw:
                self.layer.triggerRepaint()
