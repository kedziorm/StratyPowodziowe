# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Straty
                                 A QGIS plugin
 Wtyczka do obliczania sumy strat powodziowych zgodnie z Rozporządzeniem
                              -------------------
        begin                : 2015-03-22
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Mateusz Kędzior
        email                : mateusz.kedzior@is.pw.edu.pl
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from Strata_dialog import StratyDialog
import os.path
from qgis.core import QgsVectorLayer, QgsField, QgsMapLayerRegistry, QgsFeature, QgsMapLayer
from PyQt4.QtCore import QVariant 
from PyQt4.QtCore import pyqtSlot,SIGNAL,SLOT


class Straty:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Straty_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = StratyDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Obliczanie strat')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Straty')
        self.toolbar.setObjectName(u'Straty')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Straty', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Straty/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Oblicz straty'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Obliczanie strat'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

        @pyqtSlot(int)
        def onIndexChange(self, i):
                print i 

    def run(self):
        # Import additional functions:
        from MyFunctions import *
        # Bar to communicate with the user:
        msgBar = self.iface.messageBar()
        # Add items to Combobox
        layers = self.iface.legendInterface().layers()
        #################################################################################################################
        ####### TO DO ##########
        #We SHOULD check if appropriate number of vector and raster layers is correct, not only the total number
        #################################################################################################################
        if (len(layers) < 4):
                msgBar.pushMessage(u'Błąd', u'Wczytałeś mniej niż cztery warstwy do QGIS-a. Nie mogę uruchomić wtyczki - potrzebuję województwa, NMT, głębokości i ukształtowania terenu', level=msgBar.CRITICAL, duration=5)
                return
        #Add 'manually' all combo boxes to the dictionary.
        Combo = {'LandCover': self.dlg.LandCover, 'depth': self.dlg.depth, 'NMT': self.dlg.NMT, 'Voivode': self.dlg.Voivode}
        ListCombo={self.dlg.LandCover: self.dlg.LandCoverField, self.dlg.Voivode: self.dlg.VoivodeField}
        #################################################################################################################
        ####### TO DO ##########
        #We SHOULD ALLOW user to select appropriate vector fields from the selected vector layer. Currently it's hardcoded!!!
        #################################################################################################################
        #for value in ListCombo.keys():
                #value.connect(value,SIGNAL("currentIndexChanged(int)"),window,SLOT("onIndexChange(int)"))
        #Clear previously added items (if any)
        for value in Combo.itervalues():
                value.clear()
        for layer in layers:
                #for key in Combo.keys():
                for item in Combo.items():
                    if item[0] in ('Voivode'):
                        if (layer.type() == QgsMapLayer.VectorLayer):
                            item[1].addItem(layer.name(),layer)
                    elif item[0] in ('depth', 'NMT'):
                        if (layer.type() == QgsMapLayer.RasterLayer):
                            item[1].addItem(layer.name(),layer)
                    else:
                        item[1].addItem(layer.name(),layer)
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
                # Check if any value is repeated
                chosen=[]
                for value in Combo.itervalues():
                        if (value.currentText() in chosen):
                                msgBar.pushMessage(u'Błąd', u'Próbowałeś użyć warstwy ' + str(value.currentText()) + u' dla dwóch różnych warstw', level=msgBar.CRITICAL, duration=8)
                                return
                        chosen.append(value.currentText())
                # Get data from the selectors
                MyRasters = dict()
                for key in Combo.keys():
                        MyRasters[key] = Combo[key].itemData(Combo[key].currentIndex())
                # Calculate realDepth (depth - NMT)
                # About raster calculator: http://gis.stackexchange.com/questions/54949/how-to-evaluate-raster-calculator-expressions-from-the-console
                #WARNING - if your file exists, it will be replaced
                realDepth=MyRasters['depth'].dataProvider().dataSourceUri() + '.substr.tif'
                result=calculate(MyRasters['depth'],MyRasters['NMT'],'depth@1','NMT@1','NMT@1 - depth@1',realDepth)
                if (result != 0):
                       msgBar.pushMessage(u'Błąd', 'Nr błędu QgsRasterCalculator-a: ' + str(result), level=msgBar.CRITICAL, duration=8)
                       return
                #read CRS as EPSG:
                myCRS = MyRasters['depth'].crs().authid()
                #Create temporary vector layer and add to map
                vl = QgsVectorLayer("Point?crs=" + myCRS, "temporary_points", "memory")
                pr = vl.dataProvider()
                QgsMapLayerRegistry.instance().addMapLayer(vl)
                #Create dictionaries
                Majatek=dictionaryFromFile(os.path.join(self.plugin_dir,'Majatek.txt'))
                Straty=dictionaryFromFile(os.path.join(self.plugin_dir,'Funkcja_strat.txt'))
                CLCMapowanie=dictionaryFromFile(os.path.join(self.plugin_dir,'CLC_mapowanie.txt'))
                # Add points with depth and other values:
                Suma=createPointLayer(realDepth, vl, MyRasters['Voivode'],MyRasters['LandCover'],Majatek,Straty,CLCMapowanie,msgBar )

