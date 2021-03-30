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
    QgsFeatureRequest
)
from qgis.gui import (
    QgsPanelWidget,
    QgsDockWidget,
    QgsPanelWidgetStack
)

from vertex_compare.gui.gui_utils import GuiUtils
from vertex_compare.core.vertex_model import VertexModel

WIDGET, _ = uic.loadUiType(GuiUtils.get_ui_file_path('vertex_list.ui'))


class VertexListWidget(QgsPanelWidget, WIDGET):
    """
    A table for vertex lists
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setupUi(self)

        self.vertex_model = VertexModel()
        self.table_view.setModel(self.vertex_model)

        self.toolbar.addSeparator()

        self.settings_action = QAction(self.tr('Settings'), self)
        self.settings_action.setIcon(QgsApplication.getThemeIcon('/propertyicons/settings.svg'))
        self.settings_action.triggered.connect(self._show_settings)
        self.toolbar.addAction(self.settings_action)

        self.settings_panel = None
        self.layer: Optional[QgsVectorLayer] = None
        self.selection: List[int] = []

    def set_selection(self, layer: QgsVectorLayer, selection: List[int] ):
        """
        Sets the selection to show in the dock
        """
        self.layer = layer
        self.selection = selection

        if selection:
            features = self.layer.getFeatures(QgsFeatureRequest().setNoAttributes().setFilterFids(selection))
            self.vertex_model.set_feature(next(features))
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

    def __init__(self, parent=None):
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

        self.table_widget = VertexListWidget()
        self.table_widget.setDockMode(True)
        self.stack.setMainPanel(self.table_widget)

    def set_selection(self, layer: QgsVectorLayer, selection: List[int] ):
        """
        Sets the selection to show in the dock
        """
        self.table_widget.set_selection(layer, selection)