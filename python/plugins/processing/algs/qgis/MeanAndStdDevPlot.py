# -*- coding: utf-8 -*-

"""
***************************************************************************
    MeanAndStdDevPlot.py
    ---------------------
    Date                 : January 2013
    Copyright            : (C) 2013 by Victor Olaya
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

__author__ = 'Victor Olaya'
__date__ = 'January 2013'
__copyright__ = '(C) 2013, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import plotly as plt
import plotly.graph_objs as go

from qgis.core import (QgsApplication,
                       QgsFeatureSink,
                       QgsProcessingUtils)
from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm
from processing.core.parameters import ParameterTable
from processing.core.parameters import ParameterTableField
from processing.core.outputs import OutputHTML

from processing.tools import vector


class MeanAndStdDevPlot(QgisAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    NAME_FIELD = 'NAME_FIELD'
    VALUE_FIELD = 'VALUE_FIELD'

    def group(self):
        return self.tr('Graphics')

    def __init__(self):
        super().__init__()
        self.addParameter(ParameterTable(self.INPUT,
                                         self.tr('Input table')))
        self.addParameter(ParameterTableField(self.NAME_FIELD,
                                              self.tr('Category name field'), self.INPUT,
                                              ParameterTableField.DATA_TYPE_ANY))
        self.addParameter(ParameterTableField(self.VALUE_FIELD,
                                              self.tr('Value field'), self.INPUT))

        self.addOutput(OutputHTML(self.OUTPUT, self.tr('Plot')))

    def name(self):
        return 'meanandstandarddeviationplot'

    def displayName(self):
        return self.tr('Mean and standard deviation plot')

    def processAlgorithm(self, parameters, context, feedback):
        layer = QgsProcessingUtils.mapLayerFromString(self.getParameterValue(self.INPUT), context)
        namefieldname = self.getParameterValue(self.NAME_FIELD)
        valuefieldname = self.getParameterValue(self.VALUE_FIELD)

        output = self.getOutputValue(self.OUTPUT)

        values = vector.values(layer, namefieldname, valuefieldname)

        d = {}
        for i in range(len(values[namefieldname])):
            v = values[namefieldname][i]
            if v not in d:
                d[v] = [values[valuefieldname][i]]
            else:
                d[v].append(values[valuefieldname][i])

        data = []
        for k, v in d.items():
            data.append(go.Box(y=list(v),
                               boxmean='sd',
                               name=k
                               ))
        plt.offline.plot(data, filename=output, auto_open=False)
