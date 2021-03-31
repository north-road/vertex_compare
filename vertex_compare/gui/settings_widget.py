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

    extent_symbol_changed = pyqtSignal()
    label_filter_changed = pyqtSignal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setupUi(self)

        self.setPanelTitle(self.tr('Settings'))

        self.filtering_combo.addItem(self.tr('No Labels'), SettingsRegistry.LABEL_NONE)
        self.filtering_combo.addItem(self.tr('Selected Vertex Only'), SettingsRegistry.LABEL_SELECTED)
        self.filtering_combo.addItem(self.tr('All Vertices'), SettingsRegistry.LABEL_ALL)

        self.arrow_style_button.setSymbolType(QgsSymbol.Line)
        self.extent_style_button.setSymbolType(QgsSymbol.Fill)
        self.restore_settings()

        self.arrow_style_button.changed.connect(self._symbol_changed)
        self.extent_style_button.changed.connect(self._extent_symbol_changed)
        self.filtering_combo.currentIndexChanged[int].connect(self._label_filter_changed)

    def restore_settings(self):
        """
        Restores saved settings
        """
        current_label_filter = SettingsRegistry.label_filtering()
        self.filtering_combo.setCurrentIndex(self.filtering_combo.findData(current_label_filter))

        self.arrow_style_button.setSymbol(SettingsRegistry.arrow_symbol())
        self.extent_style_button.setSymbol(SettingsRegistry.extent_symbol())

    def _symbol_changed(self):
        """
        Called when the line symbol type is changed
        """
        SettingsRegistry.set_arrow_symbol(self.arrow_style_button.symbol())
        self.gcp_manager.update_line_symbols()

    def _extent_symbol_changed(self):
        """
        Called when the extent symbol type is changed
        """
        SettingsRegistry.set_extent_symbol(self.extent_style_button.symbol())
        self.extent_symbol_changed.emit()

    def _label_filter_changed(self, _: int):
        """
        Called when the label filter combobox value is changed
        """
        SettingsRegistry.set_label_filtering(
            int(self.filtering_combo.currentData())
        )
        self.label_filter_changed.emit()
