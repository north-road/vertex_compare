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

from qgis.PyQt.QtGui import (
    QColor
)
from qgis.core import (
    QgsSingleSymbolRenderer,
    QgsSymbol,
    QgsFields,
    QgsRenderContext
)


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
