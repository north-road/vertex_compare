# -*- coding: utf-8 -*-
"""QGIS Vertex Compare plugin

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

import os
from typing import (
    List,
    Optional
)

from qgis.PyQt.QtCore import (
    Qt,
    QObject,
    QTranslator,
    QCoreApplication
)
from qgis.PyQt.QtGui import (
    QFontMetrics
)
from qgis.PyQt.QtWidgets import (
    QToolBar,
    QAction
)
from qgis.core import (
    QgsApplication,
    QgsMapLayerProxyModel,
    QgsVectorLayer
)
from qgis.gui import (
    QgisInterface,
    QgsMapLayerComboBox
)

from vertex_compare.core.vertex_highlighter_manager import VertexHighlighterManager
from vertex_compare.gui.selection_handler import SelectionHandler
from vertex_compare.gui.vertex_dock import VertexDockWidget

VERSION = '0.0.1'


class VertexComparePlugin(QObject):
    """QGIS Plugin Implementation."""

    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        super().__init__()
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QgsApplication.locale()
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            '{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.toolbar = None
        self.layer_combo = None
        self.actions = []
        self.dock = None
        self.vertex_highlighter = VertexHighlighterManager()
        self.selection_handler = SelectionHandler(self)
        self.show_vertices_action = None
        self.show_dock_action = None

    @staticmethod
    def tr(message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('VertexCompare', message)

    def initProcessing(self):
        """Create the Processing provider"""

    def initGui(self):
        """Creates application GUI widgets"""
        self.initProcessing()

        self.dock = VertexDockWidget()
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.dock.setUserVisible(False)

        self.toolbar = QToolBar(self.tr('Vertex Compare Toolbar'))
        self.toolbar.setObjectName('vertexCompareToolbar')
        self.iface.addToolBar(self.toolbar)

        self.layer_combo = QgsMapLayerComboBox()
        self.layer_combo.setAllowEmptyLayer(True, self.tr('Disabled'))
        self.layer_combo.setFilters(QgsMapLayerProxyModel.PolygonLayer | QgsMapLayerProxyModel.LineLayer)
        self.layer_combo.setMinimumWidth(QFontMetrics(self.layer_combo.font()).width('x') * 40)
        self.layer_combo.setLayer(None)
        self.layer_combo.layerChanged.connect(self._set_layer)
        self.toolbar.addWidget(self.layer_combo)

        self.show_vertices_action = QAction(self.tr("Show Vertex Numbers"), self)
        self.show_vertices_action.setCheckable(True)
        self.show_vertices_action.setEnabled(False)
        self.actions.append(self.show_vertices_action)
        self.toolbar.addAction(self.show_vertices_action)
        self.show_vertices_action.toggled.connect(self.vertex_highlighter.set_visible)

        self.show_dock_action = QAction(self.tr('Show Vertices'), parent=self.toolbar)
        self.toolbar.addAction(self.show_dock_action)
        self.actions.append(self.show_dock_action)
        self.dock.setToggleVisibilityAction(self.show_dock_action)

        self.selection_handler.selection_changed.connect(self._selection_changed)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for a in self.actions:
            a.deleteLater()
        self.actions = []

        if self.toolbar is not None:
            self.toolbar.deleteLater()
            self.toolbar = None
        if self.dock is not None:
            self.dock.deleteLater()
            self.dock = None

    def _set_layer(self, layer: Optional[QgsVectorLayer]):
        """
        Triggered when the selected layer is changed
        """
        self.selection_handler.set_layer(layer)
        self.vertex_highlighter.set_layer(layer)
        self.show_vertices_action.setEnabled(layer is not None)
        if not self.show_vertices_action.isEnabled():
            self.show_vertices_action.setChecked(False)
        else:
            self.show_vertices_action.setChecked(True)

    def _selection_changed(self, layer: Optional[QgsVectorLayer], selection: List[int]):
        """
        Triggered when the watched layer's selection is changed
        """
        self.dock.set_selection(layer, selection)
