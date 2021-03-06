/************************************************************************
 * This file has been generated automatically from                      *
 *                                                                      *
 * src/analysis/raster/qgsrelief.h                                      *
 *                                                                      *
 * Do not edit manually ! Edit header and run scripts/sipify.pl again   *
 ************************************************************************/





class QgsRelief
{
%Docstring
 Produces colored relief rasters from DEM*
%End

%TypeHeaderCode
#include "qgsrelief.h"
%End
  public:
    struct ReliefColor
    {
      ReliefColor( const QColor &c, double min, double max );
      QColor color;
      double minElevation;
      double maxElevation;
    };

    QgsRelief( const QString &inputFile, const QString &outputFile, const QString &outputFormat );
    ~QgsRelief();


    int processRaster( QProgressDialog *p );
%Docstring
 Starts the calculation, reads from mInputFile and stores the result in mOutputFile
\param p progress dialog that receives update and that is checked for abort. 0 if no progress bar is needed.
:return: 0 in case of success*
 :rtype: int
%End

    double zFactor() const;
%Docstring
 :rtype: float
%End
    void setZFactor( double factor );

    void clearReliefColors();
    void addReliefColorClass( const QgsRelief::ReliefColor &color );
    QList< QgsRelief::ReliefColor > reliefColors() const;
%Docstring
 :rtype: list of QgsRelief.ReliefColor
%End
    void setReliefColors( const QList< QgsRelief::ReliefColor > &c );

    QList< QgsRelief::ReliefColor > calculateOptimizedReliefClasses();
%Docstring
 Calculates class breaks according with the method of Buenzli (2011) using an iterative algorithm for segmented regression
:return: true in case of success*
 :rtype: list of QgsRelief.ReliefColor
%End

    bool exportFrequencyDistributionToCsv( const QString &file );
%Docstring
Write frequency of elevation values to file for manual inspection
 :rtype: bool
%End

  private:
    QgsRelief( const QgsRelief &rh );
};

/************************************************************************
 * This file has been generated automatically from                      *
 *                                                                      *
 * src/analysis/raster/qgsrelief.h                                      *
 *                                                                      *
 * Do not edit manually ! Edit header and run scripts/sipify.pl again   *
 ************************************************************************/
