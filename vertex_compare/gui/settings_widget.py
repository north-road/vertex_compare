# -*- coding: utf-8 -*-
"""Settings widget

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

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    pyqtSignal
)
from qgis.PyQt.QtWidgets import (
    QWidget
)
from qgis.core import (
    QgsSymbol
)
from qgis.gui import (
    QgsPanelWidget
)

from vertex_compare.core.settings_registry import SettingsRegistry
from vertex_compare.gui.gui_utils import GuiUtils

WIDGET, _ = uic.loadUiType(GuiUtils.get_ui_file_path('settings.ui'))


class SettingsWidget(QgsPanelWidget, WIDGET):
    """
    Settings widget
    """

    vertex_symbol_changed = pyqtSignal()
    label_filter_changed = pyqtSignal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setupUi(self)

        self.setPanelTitle(self.tr('Settings'))

        self.filtering_combo.addItem(self.tr('No Labels'), SettingsRegistry.LABEL_NONE)
        self.filtering_combo.addItem(self.tr('Selected Vertex Only'), SettingsRegistry.LABEL_SELECTED)
        self.filtering_combo.addItem(self.tr('All Vertices'), SettingsRegistry.LABEL_ALL)

        self.point_symbol_button.setSymbolType(QgsSymbol.Marker)
        self.restore_settings()

        self.point_symbol_button.changed.connect(self._point_symbol_changed)
        self.filtering_combo.currentIndexChanged[int].connect(self._label_filter_changed)
        self.button_reset_defaults.clicked.connect(self._reset_settings)

    def restore_settings(self):
        """
        Restores saved settings
        """
        current_label_filter = SettingsRegistry.label_filtering()
        self.filtering_combo.setCurrentIndex(self.filtering_combo.findData(current_label_filter))

        self.point_symbol_button.setSymbol(SettingsRegistry.vertex_symbol())

    def _reset_settings(self):
        """
        Resets settings to their defaults
        """
        self.point_symbol_button.setSymbol(SettingsRegistry.default_vertex_symbol())
        SettingsRegistry.set_vertex_symbol(SettingsRegistry.default_vertex_symbol())
        self.vertex_symbol_changed.emit()

    def _point_symbol_changed(self):
        """
        Called when the marker symbol type is changed
        """
        SettingsRegistry.set_vertex_symbol(self.point_symbol_button.symbol())
        self.vertex_symbol_changed.emit()

    def _label_filter_changed(self, _: int):
        """
        Called when the label filter combobox value is changed
        """
        SettingsRegistry.set_label_filtering(
            int(self.filtering_combo.currentData())
        )
        self.label_filter_changed.emit()
