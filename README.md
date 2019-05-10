# prefactor (production version)
## The LOFAR pre-facet calibration pipeline.

**prefactor** is a pipeline to correct for various instrumental and ionospheric effects in both **LOFAR HBA** and **LOFAR LBA** observations.
It will prepare your data so that you will be able to use any direction-dependent calibration software, like [factor](https://github.com/lofar-astron/factor) or [killMS](https://github.com/saopicc/killMS/).

Note: this is the production version for use in automated processing on CEP4/LTA sites. It requires Python 3.6 or later. For the user version, see the master branch.

It includes:
* removal of clock offsets between core and remote stations (using clock-TEC separation)
* correction of the polarization alignment between XX and YY
* robust time-independent bandpass correction
* ionospheric RM corrections with [RMextract](https://github.com/lofar-astron/RMextract/)
* removal of the element beam
* advanced flagging and interpolation of bad data
* mitigation of broad-band RFI and bad stations
* direction-independent phase correction of the target, using a global sky model from [TGSS ADR](https://http://tgssadr.strw.leidenuniv.nl/)  or the new Global Sky Model [GSM](http://172.104.228.177/)
* detailled diagnostics
* (optional) wide-band cleaning with the image pipeline

The documentation can be found at the [prefactor production webpage](https://www.astron.nl/citt/prefactor_production/).

The main directory contains the different parsets for the genericpipeline:
* Pre-Facet-Calibrator.parset : The calibrator part of the "standard" pre-facet calibration pipeline.
* Pre-Facet-Target.parset : The target part of the "standard" pre-facet calibration pipeline.
* Pre-Facet-Image.parset : The imaging part of the "standard" pre-facet calibration pipeline.


The Pre-Facet-Calibration pipeline and its scripts where developed by:
* Alexander Drabent
* David Rafferty
* Andreas Horneffer
* Francesco de Gasperin
* Marco Iacobelli
* Emanuela Orru
* Björn Adebahr
* Martin Hardcastle
* George Heald
* Soumyajit Mandal
* Carole Roskowinski
* Jose Sabater Montes
* Timothy Shimwell
* Sarrvesh Sridhar
* Reinout van Weeren
* Wendy Williams

With special thanks to Stefan Fröhlich for developing the genericpipeline.

The procedure is also mostly described in these papers:
* de Gasperin, F.; Dijkema, T. J.; Drabent, A.; Mevius, M.; Rafferty, van Weeren, R., et al. 2018, [arXiv:1811.07954](http://adsabs.harvard.edu/abs/2018arXiv181107954D)
* van Weeren, R. J., Williams, W. L., Hardcastle, M. J., et al. 2016, [ApJS, 223, 2](http://adsabs.harvard.edu/abs/2016ApJS..223....2V)
* Williams, W. L., van Weeren, R. J., Röttgering, H. J. A., et al. 2016, [MNRAS, 460, 2385W](http://adsabs.harvard.edu/abs/2016MNRAS.460.2385W)


