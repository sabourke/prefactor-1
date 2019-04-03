.. Prefactor documentation master file, created by
   sphinx-quickstart on Tue Nov 27 11:30:20 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Prefactor: Preprocessing for Facet Calibration for LOFAR (Production Version)
=============================================================================

**prefactor** is a pipeline to correct for various instrumental and ionospheric effects in both **LOFAR HBA** and **LOFAR LBA** observations,
as detailed in de Gasperin, F.; Dijkema, T. J.; Drabent, A.; Mevius, M.; Rafferty, D. A.; van Weeren, R., et al. 2018, arXiv:1811.07954.

It includes:

- removal of clock offsets between core and remote stations (using clock-TEC separation)
- correction of the polarization alignment between XX and YY
- robust time-independent bandpass correction
- ionospheric RM corrections with `RMextract`_
- removal of the element beam
- advanced flagging and interpolation of bad data
- mitigation of broad-band RFI and bad stations
- direction-independent phase correction of the target, using a global sky model from `TGSS ADR`_  or the new Global Sky Model (GSM) for HBA and LBA data, respectively.
- detailled diagnostics and a summary log file

It will prepare your data so that you will be able to use any direction-dependent calibration software, like `factor`_ or `killMS`_, as well as any generic long-baseline pipeline.

.. note::

    This documentation refers to the production version, intended for automated
    processing on CEP4/LTA sites. For the user version,
    see http://www.astron.nl/citt/prefactor. The two versions are very similar, with the
    primary differences being that the production version requires that input and output
    data be specified explicitly and that metadata-feedback steps be done at the end
    (required for ingest of data products into the LTA). For more details on the differences,
    see the individual pipeline sections below. For general information on prefactor (e.g., installing,
    running, etc.), see the documentation for the user version (see link above).


The Prefactor Pipelines
-----------------------

.. toctree::
   :maxdepth: 2

   pipelineoverview
   calibrator
   target
   image


.. _TGSS ADR: https://http://tgssadr.strw.leidenuniv.nl/
.. _RMextract: https://github.com/lofar-astron/RMextract/
.. _factor: https://github.com/lofar-astron/factor/
.. _killMS: https://github.com/saopicc/killMS/
