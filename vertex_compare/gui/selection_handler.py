# -*- coding: utf-8 -*-
"""Selection handler

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
    QObject,
    pyqtSignal
)

from qgis.core import (
    QgsVectorLayer
)


class SelectionHandler(QObject):
    """
    Handles managing changes to the selected features in a watched map layer.

    Ensures that only a single layer will be watched at a time in order to avoid the performance
    impact of watching ALL layers loaded into a project
    """

    selection_changed = pyqtSignal(QgsVectorLayer, list)

    def __init__(self, parent):
        super().__init__(parent)

        self.layer: Optional[QgsVectorLayer] = None

    def set_layer(self, layer: QgsVectorLayer):
        """
        Sets the watched layer
        """
        if self.layer == layer:
            return

        if self.layer is not None:
            self.layer.selectionChanged.disconnect(self._selection_changed)

        self.layer = layer
        if self.layer is not None:
            self.layer.selectionChanged.connect(self._selection_changed)
            self.selection_changed.emit(self.layer, self.layer.selectedFeatureIds())
        else:
            self.selection_changed.emit(None, [])

    def _selection_changed(self, selected, _, __):
        """
        Called when the watched layer's selection is changed
        """
        self.selection_changed.emit(self.layer, selected)
