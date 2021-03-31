# -*- coding: utf-8 -*-
"""Settings registry

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = '(C) 2020 by Nyall Dawson'
__date__ = '29/10/2020'
__copyright__ = 'Copyright 2020, North Road'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import (
    Qt
)
from qgis.PyQt.QtGui import (
    QColor
)
from qgis.PyQt.QtXml import (
    QDomDocument
)
from qgis.core import (
    QgsApplication,
    QgsSettings,
    QgsSimpleMarkerSymbolLayer,
    QgsMarkerSymbol,
    QgsSymbolLayerUtils,
    QgsReadWriteContext,
    QgsTextFormat,
    QgsNumericFormat,
    QgsBasicNumericFormat
)


class SettingsRegistry:
    """
    Plugin settings registry
    """

    LABEL_NONE = 1
    LABEL_SELECTED = 2
    LABEL_ALL = 3

    VERTEX_SYMBOL = None
    VERTEX_FONT = None
    NUMBER_FORMAT = None

    @staticmethod
    def label_filtering() -> int:
        """
        Returns the current vertex label filtering
        """
        settings = QgsSettings()
        current_filter = settings.value('vertex_compare/labels',
                                        SettingsRegistry.LABEL_ALL,
                                        int, QgsSettings.Plugins)
        return current_filter

    @staticmethod
    def set_label_filtering(filtering: int):
        """
        Sets the current vertex label filtering
        """
        settings = QgsSettings()
        settings.setValue('vertex_compare/labels', filtering, QgsSettings.Plugins)

    @staticmethod
    def center_on_selected() -> bool:
        """
        Returns the center on selected setting
        """
        settings = QgsSettings()
        return settings.value('vertex_compare/center_on_selected',
                              False,
                              bool, QgsSettings.Plugins)

    @staticmethod
    def set_center_on_selected(center: bool):
        """
        Sets whether the map should be centered on the selected vertex automatically
        """
        settings = QgsSettings()
        settings.setValue('vertex_compare/center_on_selected', center, QgsSettings.Plugins)

    @staticmethod
    def default_vertex_symbol() -> QgsMarkerSymbol:
        """
        Returns the default marker symbol to use for vertices
        """
        symbol = QgsMarkerSymbol()
        simple_marker = QgsSimpleMarkerSymbolLayer(QgsSimpleMarkerSymbolLayer.Circle)
        simple_marker.setSize(1)
        simple_marker.setStrokeStyle(Qt.NoPen)
        symbol.changeSymbolLayer(0, simple_marker)
        return symbol

    @staticmethod
    def vertex_symbol() -> QgsMarkerSymbol:
        """
        Returns the marker symbol to use for vertices
        """
        if SettingsRegistry.VERTEX_SYMBOL is not None:
            return SettingsRegistry.VERTEX_SYMBOL.clone()

        settings = QgsSettings()
        symbol_doc = settings.value('vertex_compare/marker_symbol', '', str, QgsSettings.Plugins)
        if not symbol_doc:
            SettingsRegistry.VERTEX_SYMBOL = SettingsRegistry.default_vertex_symbol()
        else:
            doc = QDomDocument()
            doc.setContent(symbol_doc)
            SettingsRegistry.VERTEX_SYMBOL = QgsSymbolLayerUtils.loadSymbol(doc.documentElement(),
                                                                            QgsReadWriteContext())

        return SettingsRegistry.VERTEX_SYMBOL.clone()

    @staticmethod
    def set_vertex_symbol(symbol: QgsMarkerSymbol):
        """
        Sets the marker symbol to use for vertices
        """
        SettingsRegistry.VERTEX_SYMBOL = symbol.clone()

        doc = QDomDocument()
        elem = QgsSymbolLayerUtils.saveSymbol('vertex', symbol, doc, QgsReadWriteContext())
        doc.appendChild(elem)

        settings = QgsSettings()
        settings.setValue('vertex_compare/marker_symbol', doc.toString(), QgsSettings.Plugins)

    @staticmethod
    def default_vertex_format() -> QgsTextFormat:
        """
        Returns the default text format to use for vertices
        """
        text_format = QgsTextFormat()
        text_format.setSize(10)
        text_format.setNamedStyle('Bold')
        text_format.buffer().setEnabled(True)
        text_format.buffer().setColor(QColor(255, 255, 255))
        return text_format

    @staticmethod
    def vertex_format() -> QgsTextFormat:
        """
        Returns the text format to use for vertices
        """
        if SettingsRegistry.VERTEX_FONT is not None:
            return SettingsRegistry.VERTEX_FONT

        settings = QgsSettings()
        format_doc = settings.value('vertex_compare/vertex_font', '', str, QgsSettings.Plugins)
        if not format_doc:
            SettingsRegistry.VERTEX_FONT = SettingsRegistry.default_vertex_format()
        else:
            doc = QDomDocument()
            doc.setContent(format_doc)
            SettingsRegistry.VERTEX_FONT = QgsTextFormat()
            SettingsRegistry.VERTEX_FONT.readXml(doc.documentElement(), QgsReadWriteContext())

        return QgsTextFormat(SettingsRegistry.VERTEX_FONT)

    @staticmethod
    def set_vertex_format(text_format: QgsTextFormat):
        """
        Sets the text format to use for vertices
        """
        SettingsRegistry.VERTEX_FONT = QgsTextFormat(text_format)

        doc = QDomDocument()
        elem = text_format.writeXml(doc, QgsReadWriteContext())
        doc.appendChild(elem)

        settings = QgsSettings()
        settings.setValue('vertex_compare/vertex_font', doc.toString(), QgsSettings.Plugins)

    @staticmethod
    def default_number_format() -> QgsNumericFormat:
        """
        Returns the default number format to use for coordinates
        """
        number_format = QgsBasicNumericFormat()
        number_format.setNumberDecimalPlaces(10)
        number_format.setShowThousandsSeparator(False)
        return number_format

    @staticmethod
    def number_format() -> QgsNumericFormat:
        """
        Returns the default number format to use for coordinates
        """
        if SettingsRegistry.NUMBER_FORMAT is not None:
            return SettingsRegistry.NUMBER_FORMAT

        settings = QgsSettings()
        format_doc = settings.value('vertex_compare/number_format', '', str, QgsSettings.Plugins)
        if not format_doc:
            SettingsRegistry.NUMBER_FORMAT = SettingsRegistry.default_number_format()
        else:
            doc = QDomDocument()
            doc.setContent(format_doc)
            SettingsRegistry.NUMBER_FORMAT = QgsApplication.numericFormatRegistry().createFromXml(doc.documentElement(),
                                                                                                  QgsReadWriteContext())

        return SettingsRegistry.NUMBER_FORMAT.clone()

    @staticmethod
    def set_number_format(number_format: QgsNumericFormat):
        """
        Sets the number format to use for coordinates
        """
        SettingsRegistry.NUMBER_FORMAT = number_format.clone()

        doc = QDomDocument()
        elem = doc.createElement('format')
        number_format.writeXml(elem, doc, QgsReadWriteContext())
        doc.appendChild(elem)

        settings = QgsSettings()
        settings.setValue('vertex_compare/number_format', doc.toString(), QgsSettings.Plugins)


SETTINGS_REGISTRY = SettingsRegistry()
