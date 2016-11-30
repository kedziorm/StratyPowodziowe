# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Straty
                                 A QGIS plugin
 Wtyczka do obliczania sumy strat powodziowych
                             -------------------
        begin                : 2015-03-22
        copyright            : (C) 2015 by Mateusz Kędzior
        email                : mateusz.kedzior@is.pw.edu.pl
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Straty class from file Straty.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Strata import Straty
    return Straty(iface)
