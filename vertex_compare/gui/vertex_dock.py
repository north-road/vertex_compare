# -*- coding: utf-8 -*-
"""Dock widget

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = '(C) 2018 by Nyall Dawson'
__date__ = '20/04/2018'
__copyright__ = 'Copyright 2018, North Road'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from typing import (
    List,
    Optional
)

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QAction
)
from qgis.core import (
    QgsApplication,
    QgsVectorLayer,
    QgsCoordinateTransform,
    QgsProject,
    QgsCsException
)
from qgis.gui import (
    QgsPanelWidget,
    QgsDockWidget,
    QgsPanelWidgetStack,
    QgsMapCanvas
)

from vertex_compare.core.feature_model import FeatureModel
from vertex_compare.core.vertex_model import VertexModel
from vertex_compare.gui.gui_utils import GuiUtils

WIDGET, _ = uic.loadUiType(GuiUtils.get_ui_file_path('vertex_list.ui'))


class VertexListWidget(QgsPanelWidget, WIDGET):
    """
    A table for vertex lists
    """

    def __init__(self, map_canvas: QgsMapCanvas, parent: QWidget = None):
        super().__init__(parent)

        self.setupUi(self)

        self._block_feature_changes = False

        self.map_canvas = map_canvas

        self.vertex_model = VertexModel()
        self.table_view.setModel(self.vertex_model)

        self.feature_model = FeatureModel()
        self.feature_combo.setModel(self.feature_model)
        self.feature_combo.currentIndexChanged.connect(self._active_feature_changed)

        self.toolbar.addSeparator()

        self.settings_action = QAction(self.tr('Settings'), self)
        self.settings_action.setIcon(QgsApplication.getThemeIcon('/propertyicons/settings.svg'))
        self.settings_action.triggered.connect(self._show_settings)
        self.toolbar.addAction(self.settings_action)

        self.settings_panel = None
        self.layer: Optional[QgsVectorLayer] = None
        self.selection: List[int] = []

        self.button_zoom.clicked.connect(self._zoom_to_feature)

    def set_selection(self, layer: QgsVectorLayer, selection: List[int]):
        """
        Sets the selection to show in the dock
        """
        if layer == self.layer:
            prev_feature_id = self.feature_model.data(self.feature_model.index(self.feature_combo.currentIndex(), 0),
                                                      FeatureModel.FEATURE_ID_ROLE)
        else:
            prev_feature_id = None

        self.layer = layer
        self.layer_label.setText(
            self.tr('{} — {} features selected').format(layer.name(), layer.selectedFeatureCount()))

        self._block_feature_changes = True

        self.selection = selection
        self.feature_model.set_feature_ids(layer, selection)

        if prev_feature_id is not None:
            prev_index = self.feature_model.index_from_id(prev_feature_id)
            if prev_index.isValid():
                self.feature_combo.setCurrentIndex(self.feature_model.index_from_id(prev_feature_id).row())
            else:
                self.feature_combo.setCurrentIndex(0)
        else:
            self.feature_combo.setCurrentIndex(0)

        self._block_feature_changes = False

        self._active_feature_changed()

    def _active_feature_changed(self):
        """
        Triggered when the active feature is changed
        """
        if self._block_feature_changes:
            return

        selected_index = self.feature_model.index(self.feature_combo.currentIndex(), 0)
        if selected_index.isValid():
            feature = self.feature_model.data(selected_index, FeatureModel.FEATURE_ROLE)
            changed = self.vertex_model.feature is None or feature is None or self.vertex_model.feature.id() != feature.id()
            self.vertex_model.set_feature(feature)
            if changed and feature is not None:
                self.map_canvas.flashGeometries([feature.geometry()], self.layer.crs())
        else:
            self.vertex_model.set_feature(None)

    def _show_settings(self):
        """
        Shows the settings panel
        """
        self.settings_panel = SettingsWidget()
        self.settings_panel.panelAccepted.connect(self._update_settings)
        self.openPanel(self.settings_panel)

    def _update_settings(self):
        """
        Updates the stored settings
        """
        self.settings_panel.deleteLater()
        self.settings_panel = None

    def _zoom_to_feature(self):
        """
        Zooms to the extent of the selected feature
        """
        selected_index = self.feature_model.index(self.feature_combo.currentIndex(), 0)
        if selected_index.isValid():
            feature = self.feature_model.data(selected_index, FeatureModel.FEATURE_ROLE)

            ct = QgsCoordinateTransform(self.layer.crs(), self.map_canvas.mapSettings().destinationCrs(),
                                        QgsProject.instance())
            try:
                bounds = ct.transformBoundingBox(feature.geometry().boundingBox())
                self.map_canvas.zoomToFeatureExtent(bounds)
            except QgsCsException:
                pass


SETTINGS_WIDGET, _ = uic.loadUiType(GuiUtils.get_ui_file_path('settings.ui'))


class SettingsWidget(QgsPanelWidget, SETTINGS_WIDGET):
    """
    Settings configuration widget
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setupUi(self)

        self.setPanelTitle(self.tr('Settings'))

        self.restore_settings()

    def restore_settings(self):
        """
        Restores saved settings
        """


class VertexDockWidget(QgsDockWidget):
    """
    A dock widget container for plugin GUI components
    """

    def __init__(self, map_canvas: QgsMapCanvas, parent=None):
        super().__init__(parent)

        self.setObjectName('VertexCompareDockWidget')
        self.setWindowTitle(self.tr('Vertices'))

        self.stack = QgsPanelWidgetStack()

        w = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.stack)
        w.setLayout(layout)
        self.setWidget(w)

        self.table_widget = VertexListWidget(map_canvas)
        self.table_widget.setDockMode(True)
        self.stack.setMainPanel(self.table_widget)

    def set_selection(self, layer: QgsVectorLayer, selection: List[int]):
        """
        Sets the selection to show in the dock
        """
        self.table_widget.set_selection(layer, selection)
