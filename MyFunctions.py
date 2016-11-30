# -*- coding: utf-8 -*-
from osgeo import osr
from osgeo import gdal
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
from qgis.core import QgsVectorLayer, QgsField, QgsMapLayerRegistry, QgsFeature, QgsGeometry, QgsPoint, QgsMapLayer
from PyQt4.QtCore import QVariant  

def calculate(raster1,raster2,raster1ref,raster2ref,calculation,output):
	#for example: calculation: 'boh@1 + boh@2', output: '/home/user/outputfile.tif'

	entries = []
	# Define band1
	boh1 = QgsRasterCalculatorEntry()
	boh1.ref = raster1ref
	boh1.raster = raster1
	boh1.bandNumber = 1
	entries.append( boh1 )

	# Define band2
	boh2 = QgsRasterCalculatorEntry()
	boh2.ref = raster2ref
	boh2.raster = raster2
	boh2.bandNumber = 1
	entries.append( boh2 )

	if (raster1.width() < raster2.width()):
		bohLayer = raster1
	else:
		bohLayer = raster2

	# Process calculation with input extent and resolution
	calc = QgsRasterCalculator( calculation, output ,'GTiff', bohLayer.extent(), bohLayer.width(), bohLayer.height(), entries )
	m=calc.processCalculation()
	return m

def isfloat(value):
	try:
		float(value)
		return True
	except TypeError:
		return False
	except ValueError:
		return False


def createPointLayer(RasterfilePath, PointLayer, WojewodztwoVector, CLCRaster, Majatek,Straty,CLCMapowanie, msgBar):
	#################################################################################################################
	####### TO DO ##########
	# This function do most of the plugin job. It should be highly refactored.
	#FOR SURE HANDLING OF NULL/None values must be reimplemented!!!!!!
	#################################################################################################################
	import wx
	#import numpy
	#needs to measure time
	import datetime
	start=datetime.datetime.now()
	from osgeo import gdal
	from PyQt4.QtCore import *

	pr = PointLayer.dataProvider()

	# Enter editing mode
	PointLayer.startEditing()

	# add fields
	pr.addAttributes( [ QgsField(u"Głębokość", QVariant.Double),
		QgsField(u"Województwo",  QVariant.String),
		QgsField(u"typ_zab", QVariant.String),
		QgsField("Wi", QVariant.Double),
		QgsField("fs", QVariant.Double),
		QgsField("powierzchnia", QVariant.Double),
		QgsField(u"Czas obliczeń", QVariant.Double),
		QgsField("StrataPiksela", QVariant.Double) ] )

	raster_or = gdal.Open(RasterfilePath)

	nodata = raster_or.GetRasterBand(1).GetNoDataValue()
	(upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = raster_or.GetGeoTransform()

	numpy_array = raster_or.ReadAsArray()

	#Since wi is per square meter, we change degrees to meters (1 degree is approximately equal to 111196,672 m):
	PixelArea = abs(float((x_size*111197)*(y_size*111197)))

	Suma=0
	#width,height = numpy_array.shape
	width=raster_or.GetRasterBand(1).XSize
	height=raster_or.GetRasterBand(1).YSize

	CLClist = prepareRaster(CLCRaster)
	SlownikStrat=dict()
	for row in range(0,height): #przy wartościach 150 (height, row) i 400 (width, col) już się krztusi
		for col in range(0,width):
			if  (~(nodata==numpy_array[row,col])) and (numpy_array[row,col] >0):
				#Check how much time elapsed:
				elapsed = float((datetime.datetime.now() - start).seconds)
				if (elapsed > 300):
					msgBar.pushMessage(u'Błąd',u'Obliczenia trwają dłużej niż pięc minut. Przerywam pracę.', level=msgBar.CRITICAL, duration=8)
					return Suma
				#Add new point:
				x = col * x_size + upper_left_x + (x_size / 2) #add half the cell size
				y = row * y_size + upper_left_y + (y_size / 2) #to centre the point
				#Get wojewodztwo:
				glebokosc=float(numpy_array[row,col])
				wojewodztwo=valueFromPolygon(WojewodztwoVector, x, y, 'VARNAME_1')
				if (CLCRaster.type() == QgsMapLayer.VectorLayer):
					typ_zab=valueFromPolygon(CLCRaster, x, y, 'typ_zab')
				else:
					typ_zab=getKlasa(CLCMapowanie,valueFromRaster(CLClist[0],CLClist[1],CLClist[2],CLClist[3],CLClist[4],CLClist[5],CLClist[6],CLClist[7],CLClist[8], x, y))#).encode("utf-8")
				#msgBar.pushMessage(u'Dane:', str(typ_zab) + '     ' + str(glebokosc), level=msgBar.CRITICAL, duration=8)
				test = getMajatek(Majatek,typ_zab,wojewodztwo)
				if isfloat(test):
					Wi=float(test)
				else:
					Wi=float(0)
				test=getStrata(Straty,typ_zab,glebokosc)
				if isfloat(test):
					fs=float(test)/100
				else:
					fs=float(0)
				StrataPiksela=Wi*PixelArea*fs
				#
				if typ_zab in SlownikStrat.keys():
					try:
						SlownikStrat[typ_zab]=SlownikStrat[typ_zab] + StrataPiksela
					except:
						pass
				else:
					SlownikStrat[typ_zab]=StrataPiksela
				Suma=Suma+StrataPiksela
				# add a feature
				fet = QgsFeature()
				fet.setGeometry( QgsGeometry.fromPoint(QgsPoint(x,y) ))
				fet.initAttributes(8)
				fet.setAttribute(0, glebokosc)
				fet.setAttribute(1, wojewodztwo)
				fet.setAttribute(2, typ_zab)
				fet.setAttribute(3, Wi)
				fet.setAttribute(4, fs)
				fet.setAttribute(5, PixelArea)
				fet.setAttribute(6, elapsed)
				fet.setAttribute(7, StrataPiksela)
				pr.addFeatures( [ fet ] )
	# Commit changes
	PointLayer.commitChanges()
	tekst=""
	for row in SlownikStrat.keys():
		try:
			tekst = tekst + row + ": " + str(SlownikStrat[row]) + "\n"
		except:
			pass
	#Show results:
	app = wx.App(False)
	komunikat="\n".join(["Zakończono obliczenia po czasie: " + str(elapsed) + "sekund", "Straty w poszczególnych klasach", tekst,"Całkowita suma: " + str(Suma)])
	wx.MessageBox(komunikat,"Wynik")
	#Return sum:
	#return Suma

def dictionaryFromFile(filepath):
	import os
	sep="\t"
	if (os.path.isfile(filepath)):
		# Only if file not empty:
		if (os.stat(filepath).st_size > 0):
			temp=open(filepath,'r')
			lines=temp.readlines()
			temp.close()
			#read number of columns
			col=len(lines[0].split(sep))
			#create empty dictionary:
			mydict=dict()
			#do the job:
			for line in lines:
				line_sp=(line.rstrip()).split(sep)
				if (len(line_sp) == col):
					mykeys=[]
					for i in range(0,col-1):
						mykeys.append(line_sp[i])
					mydict[tuple(mykeys)]=line_sp[col-1]
				else:
					print("Number of columns in following line is different than in the first one:")
					print(line)
					return
			return mydict
	else:
		print("Incorrect file path or this is not a file!!")

def getStrata(slownik,typ_zab,glebokosc):
	Strata=None
	for row in slownik:
		try:
			warunek=(str(row[0]).lower() == typ_zab.lower()) and (float(glebokosc) >= float(row[1])) and (float(glebokosc) < float(row[2]))
		except:
			warunek=False
		if (warunek):
			Strata = slownik[row]
	return Strata


def getMajatek(slownik,typ_zab,wojewodztwo):
	Majatek=None
	for row in slownik:
		try:
			warunek=(str(row[0]).lower() == typ_zab.lower()) and (wojewodztwo.lower() == str(row[1]).lower())
		except:
			warunek=False
		if (warunek):
			Majatek = slownik[row]
	return Majatek

def getKlasa(slownik,wartosc):
	Klasa=None
	for row in slownik:
		if (str(row[0]) == str(wartosc) ):
			Klasa= slownik[row]
	return Klasa


def valueFromPolygon(polygonlayer, x, y, attribute):
	Value=None
	features = polygonlayer.dataProvider().getFeatures()
	for feature in features: 
		if (feature.geometry().contains(QgsGeometry.fromPoint(QgsPoint(x, y)))): 
			Value = feature.attribute(attribute)
	features.close()
	return Value

def prepareRaster(Rasterlayer):
	#################################################################################################################
	####### TO DO ##########
	#PLEASE NOTE - WE ASSUME THAT RASTER IS IN THE SAME CRS AS x AND y!!!!!
	#This should be handled properly.
	#################################################################################################################
	#Get GeoTransform
	if  (Rasterlayer.type() == QgsMapLayer.RasterLayer):
		ds = gdal.Open(Rasterlayer.dataProvider().dataSourceUri())
		(upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = ds.GetGeoTransform()
		#Read raster as array:
		numpy_array = ds.ReadAsArray()
		#
		width=ds.GetRasterBand(1).XSize
		height=ds.GetRasterBand(1).YSize
		return [numpy_array,width,height,upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size]
	else:
		print u'To nie jest warstwa rastrowa!'
		return None

def valueFromRaster(numpy_array,width,height,upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size, x, y):
	col = int((x-upper_left_x)/x_size)
	row = int((y-upper_left_y)/y_size)
	#
	if (row <= height) and (col <= width):
		return numpy_array[row,col]
	else:
		print u'X:' + str(x) + u' przeliczono na kolumnę rastra: ' + str(col) + u'. Szerokość całego rastra: ' + str(width)
		print u'Y:' + str(y) + u' przeliczono na następujący wiersz: ' + str(row) + u'. Wysokość całego rastra: ' + str(height)
		print u'Sprawdź, czy używasz tego samego układu współrzędnych!!'
		return None

