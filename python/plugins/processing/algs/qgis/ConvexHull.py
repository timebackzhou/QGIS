# -*- coding: utf-8 -*-

"""
***************************************************************************
    ConvexHull.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from builtins import str

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QVariant

from qgis.core import (QgsField,
                       QgsFeature,
                       QgsFeatureSink,
                       QgsGeometry,
                       QgsWkbTypes,
                       QgsProcessingUtils,
                       QgsFields)

from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.core.parameters import ParameterVector
from processing.core.parameters import ParameterTableField
from processing.core.parameters import ParameterSelection
from processing.core.outputs import OutputVector
from processing.tools import dataobjects, vector

pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]


class ConvexHull(QgisAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    FIELD = 'FIELD'
    METHOD = 'METHOD'

    def icon(self):
        return QIcon(os.path.join(pluginPath, 'images', 'ftools', 'convex_hull.png'))

    def group(self):
        return self.tr('Vector geometry tools')

    def __init__(self):
        super().__init__()
        self.methods = [self.tr('Create single minimum convex hull'),
                        self.tr('Create convex hulls based on field')]

        self.addParameter(ParameterVector(self.INPUT,
                                          self.tr('Input layer')))
        self.addParameter(ParameterTableField(self.FIELD,
                                              self.tr('Field (optional, only used if creating convex hulls by classes)'),
                                              self.INPUT, optional=True))
        self.addParameter(ParameterSelection(self.METHOD,
                                             self.tr('Method'), self.methods))
        self.addOutput(OutputVector(self.OUTPUT, self.tr('Convex hull'), datatype=[dataobjects.TYPE_VECTOR_POLYGON]))

    def name(self):
        return 'convexhull'

    def displayName(self):
        return self.tr('Convex hull')

    def processAlgorithm(self, parameters, context, feedback):
        layer = QgsProcessingUtils.mapLayerFromString(self.getParameterValue(self.INPUT), context)
        useField = self.getParameterValue(self.METHOD) == 1
        fieldName = self.getParameterValue(self.FIELD)

        f = QgsField('value', QVariant.String, '', 255)
        if useField:
            index = layer.fields().lookupField(fieldName)
            fType = layer.fields()[index].type()
            if fType in [QVariant.Int, QVariant.UInt, QVariant.LongLong, QVariant.ULongLong]:
                f.setType(fType)
                f.setLength(20)
            elif fType == QVariant.Double:
                f.setType(QVariant.Double)
                f.setLength(20)
                f.setPrecision(6)
            else:
                f.setType(QVariant.String)
                f.setLength(255)

        fields = QgsFields()
        fields.append(QgsField('id', QVariant.Int, '', 20))
        fields.append(f)
        fields.append(QgsField('area', QVariant.Double, '', 20, 6))
        fields.append(QgsField('perim', QVariant.Double, '', 20, 6))

        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(fields, QgsWkbTypes.Polygon, layer.crs(), context)

        outFeat = QgsFeature()
        inGeom = QgsGeometry()
        outGeom = QgsGeometry()

        fid = 0
        val = None
        features = QgsProcessingUtils.getFeatures(layer, context)
        if useField:
            unique = layer.uniqueValues(index)
            current = 0
            total = 100.0 / (layer.featureCount() * len(unique)) if layer.featureCount() else 1
            for i in unique:
                first = True
                hull = []
                features = QgsProcessingUtils.getFeatures(layer, context)
                for f in features:
                    idVar = f[fieldName]
                    if str(idVar).strip() == str(i).strip():
                        if first:
                            val = idVar
                            first = False

                        inGeom = f.geometry()
                        points = vector.extractPoints(inGeom)
                        hull.extend(points)
                    current += 1
                    feedback.setProgress(int(current * total))

                if len(hull) >= 3:
                    tmpGeom = QgsGeometry(outGeom.fromMultiPoint(hull))
                    try:
                        outGeom = tmpGeom.convexHull()
                        (area, perim) = vector.simpleMeasure(outGeom)
                        outFeat.setGeometry(outGeom)
                        outFeat.setAttributes([fid, val, area, perim])
                        writer.addFeature(outFeat, QgsFeatureSink.FastInsert)
                    except:
                        raise GeoAlgorithmExecutionException(
                            self.tr('Exception while computing convex hull'))
                fid += 1
        else:
            hull = []
            total = 100.0 / layer.featureCount() if layer.featureCount() else 1
            features = QgsProcessingUtils.getFeatures(layer, context)
            for current, f in enumerate(features):
                inGeom = f.geometry()
                points = vector.extractPoints(inGeom)
                hull.extend(points)
                feedback.setProgress(int(current * total))

            tmpGeom = QgsGeometry(outGeom.fromMultiPoint(hull))
            try:
                outGeom = tmpGeom.convexHull()
                (area, perim) = vector.simpleMeasure(outGeom)
                outFeat.setGeometry(outGeom)
                outFeat.setAttributes([0, 'all', area, perim])
                writer.addFeature(outFeat, QgsFeatureSink.FastInsert)
            except:
                raise GeoAlgorithmExecutionException(
                    self.tr('Exception while computing convex hull'))

        del writer
