# prefactor
## The LOFAR pre-facet calibration pipeline.

**prefactor** is a pipeline to correct for various instrumental and ionospheric effects in both **LOFAR HBA** and **LOFAR LBA** observations.
It will prepare your data so that you will be able to use any direction-dependent calibration software, like [factor](https://github.com/lofar-astron/factor) or [killMS](https://github.com/saopicc/killMS/).

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
* (optional) wide-band cleaning in Initial-Subtract

The full documentation can be found at the [prefactor webpage](https://www.astron.nl/citt/prefactor/).

### Software requirements:
* the full "offline" LOFAR software installation (version >= 3.1)
* [LoSoTo](https://github.com/revoltek/losoto) (version >= 2.0)
* [LSMTool](https://github.com/darafferty/LSMTool)
* [RMextract](https://github.com/maaijke/RMextract)
* Python (including matplotlib, scipy, and astropy)
* [AOFlagger](https://sourceforge.net/p/aoflagger/wiki/Home/)
* [WSClean](https://sourceforge.net/projects/wsclean) (for Initial-Subtract; version >= 2.5)
* for Initial-Subtract-IDG(-LowMemory).parset: WSClean must be compiled with IDG (see https://gitlab.com/astron-idg/idg)
* APLpy (for Initial-Subtract)

### Installation
The recommended way to install prefactor is to download it from github with:

```
git clone https://github.com/lofar-astron/prefactor.git
```

This allows for easy updating of the code to include bugfixes or new features.
It is also possible to download tar files of releases from the [release page](https://github.com/lofar-astron/prefactor/releases).

Once downloaded, the installation is complete; to set up a run, see the detailed setup information at the [prefactor webpage](https://www.astron.nl/citt/prefactor/).

### Directory Structure
prefactor contains the following sub-directories:
* **bin** scripts for your convenience. At the moment, these consist only of a state-file manipulation tool for changing the state of a previously run pipeline
* **plugins** scripts for manipulating mapfiles
* **skymodels** skymodels that are used by the pipeline (e.g. for demixing or calibrating the calibrator)
* **scripts** scripts that the pipeline calls to process data, generate plots, etc.

The main directory contains the different parsets for the genericpipeline:
* Pre-Facet-Calibrator.parset : The calibrator part of the "standard" pre-facet calibration pipeline.
* Pre-Facet-Target.parset : The target part of the "standard" pre-facet calibration pipeline.
* Initial-Subtract.parset : A pipeline that generates full FoV images and subtracts the sky-models from the visibilities. (Needed for facet-calibration.)
* Initial-Subtract-IDG.parset : Same as Initial-Subtract-Fast.parset, but uses the image domain gridder (IDG) in WSClean
* Initial-Subtract-IDG-LowMemory.parset : Same as Initial-Subtract-Fast.parset, but uses the image domain gridder (IDG) in WSClean for high-res imaging


The Pre-Facet-Calibration pipeline and its scripts where developed by:
* Alexander Drabent <alex somewhere tls-tautenburg.de>
* Martin Hardcastle <mjh somewhere extragalactic.info>
* George Heald <heald somewhere astron.nl>
* Andreas Horneffer <ahorneffer somewhere mpifr-bonn.mpg.de>
* Soumyajit Mandal <mandal somewhere strw.leidenuniv.nl>
* David Rafferty <drafferty somewhere hs.uni-hamburg.de>
* Carole Roskowinski <carosko gmail.com>
* Jose Sabater Montes <jsm somewhere iaa.es>
* Timothy Shimwell <shimwell somewhere strw.leidenuniv.nl>
* Sarrvesh Sridhar <sarrvesh somewhere astro.rug.nl>
* Reinout van Weeren <rvweeren somewhere strw.leidenuniv.nl>
* Wendy Williams <wwilliams somewhere strw.leidenuniv.nl>

With special thanks to Stefan Fröhlich for developing the genericpipeline.

The procedure is also mostly described in these papers:
* de Gasperin, F.; Dijkema, T. J.; Drabent, A.; Mevius, M.; Rafferty, van Weeren, R., et al. 2018, [arXiv:1811.07954](http://adsabs.harvard.edu/abs/2018arXiv181107954D)
* van Weeren, R. J., Williams, W. L., Hardcastle, M. J., et al. 2016, [ApJS, 223, 2](http://adsabs.harvard.edu/abs/2016ApJS..223....2V)
* Williams, W. L., van Weeren, R. J., Röttgering, H. J. A., et al. 2016, [MNRAS, 460, 2385W](http://adsabs.harvard.edu/abs/2016MNRAS.460.2385W)


