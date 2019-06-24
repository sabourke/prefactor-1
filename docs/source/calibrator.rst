.. _calibrator_pipeline:

Calibrator pipeline
===================

This pipeline processes the calibrator data in order to derive direction-independent corrections.
It will take into account the correct order of distortions to be calibrated for.
This chapter will present the specific steps of the calibrator pipeline in more detail.
You will find the single steps in the parameter ``pipeline.steps``.
All results (diagnostic plots and calibration solutions) are usually stored in a subfolder of the results directory, see ``inspection_directory`` and ``cal_values_directory``, respectively.

    .. note::

        In the following, example plots are shown for a well-behaved HBA calibration run. Results that differ significantly from these may indicate problems with the calibration and should be investigated in more detail if possible.

    .. image:: calibscheme.png

Prepare calibrator
------------------

This part of the pipeline prepares the calibrator data in order to be calibration-ready.
This mainly includes mitigation of bad data (RFI, bad antennas, contaminations from A-Team sources), selection of the data to be calibrated (usually Dutch stations only), and some averaging to reduce data size and enhance the signal-to-noise ratio.
The pipeline must be run on pre-processed data only.

The basic steps are:

- mapping of data to be used (``cal_input_filenames``).
- check of A-team relation to target: plot of the elevation of the calibrator and A-team sources (plus the Sun, Jupiter, and the Moon) versus time (``check_Ateam_separation``).
    .. image:: A-Team_elevation_calibrator.png
- creating a model of A-Team sources to be subtracted (``make_sourcedb_ateam``). This step is not currently used.
- basic flagging and averaging (``ndppp_prep_cal``).
    - edges of the band (``flagedge``) -- only used in ``raw_flagging`` mode.
    - statistical flagging (``aoflag``) -- only used in ``raw_flagging`` mode.
    - baseline flagging (``flag``).
    - low elevation flagging (below 20 degress elevation) (``elev``).
    - demix A-Team sources (``demix``). This step is not currently used.
    - interpolation of flagged data (``interp``).
    - averaging of the data to 4 sec and 4 channels per subband (``avg``).
- wide-band statistical flagging (``aoflag``).
- find needed sky model of calibrator automatically (``sky_cal``).
- write the calibrator sky model into the MODEL_DATA column (``predict_cal``).
- interpolate flagged data from the wide-band statistical flagging step (``interp_cal``).
- baseline-dependent smoothing of the data (``smooth_data``).
- perform direction-independent phase-only calibration. In the first two calibrations, both diagonal terms and a common rotation angle are solved for (``calib_cal``). In the third and forth calibrations, after correction for Faraday rotation, only the diagonal terms are solved for (``calib_cal2``).

All solutions are stored in the h5parm file format.

Calibration of the polarization alignment (PA)
----------------------------------------------
The phase solutions derived from the preparation step are now collected and loaded into **LoSoTo**.
**LoSoTo** will derive the polarization alignment and provide diagnostic plots:

- ``polalign_ph_pol??``: matrix plot of the phase solutions for the XX and YY polarization.
    .. image:: polalign_ph_polXX.png
- ``polalign_ph_poldif``: matrix plot of the phase solutions from XX-YY.
    .. image:: polalign_ph_poldif.png
- ``polalign_rotange``: matrix plot of the common rotation angle solutions.
    .. image:: polalign_rotangle.png
- ``polalign_amp_pol??``: matrix plot of the amplitude solutions for the XX and YY polarization.
    .. image:: polalign_amp_polXX.png
- ``polalign``: matrix plot of the derived polarization alignment between XX and YY.
    .. image:: polalign.png
- ``polalign_ph-res_pol??``: matrix plot of the residual phase solutions for the XX and YY polarization after subtraction the derived polarization alignment.
    .. image:: polalign_ph-res_polXX.png
- ``polalign_ph-res_poldif``: matrix plot of the residual phase solutions for XX-YY after subtraction of the derived polarization alignment.
    .. image:: polalign_ph-res_poldif.png

The solutions are then stored in the final calibrator solution set ``cal_solutions`` and applied to the interpolated data (``apply_PA``), together with the LOFAR beam correction (``apply_beam``).
The calibration (``calib_cal``) is then continued on the polarization-alignment corrected and re-smoothed data (``smooth_corrected``).

Calibration of the Faraday rotation (FR)
----------------------------------------
The outcome of the re-calibration **after** correcting for the polarization alignment is again loaded into **LoSoTo** in order to derive corrections for Faraday rotation.
The following diagnostic plots are created:

- ``fr_ph_pol??``: matrix plot of the phase solutions for the XX and YY polarization.
   .. image:: fr_ph_polXX.png
- ``fr_ph_poldif``: matrix plot of the phase solutions from XX-YY.
   .. image:: fr_ph_poldif.png
- ``fr_rotangle``: matrix plot of the common rotation angle solutions.
   .. image:: fr_rotangle.png
- ``fr_amp_pol??``: matrix plot of the amplitude solutions for the XX and YY polarization.
   .. image:: fr_amp_polXX.png
- ``fr``: matrix plot of the derived differential rotation measure (dRM) from Faraday rotation.
    .. image:: fr.png
- ``fr_ph-res_pol??``: matrix plot of the residual phase solutions for the XX and YY polarization after subtraction the derived differential rotation measure.
   .. image:: fr_ph-res_polXX.png
- ``fr_ph-res_poldif``: matrix plot of the residual phase solutions for XX-YY after subtraction of the derived differential rotation measure.
   .. image:: fr_ph-res_poldif.png

The solutions are then stored in the final calibrator solution set ``cal_solutions`` and applied, together with the polarization alignment and the LOFAR beam correction, to the interpolated data (``apply_PA`` + ``apply_beam`` + ``apply_FR``).
The calibration (``calib_cal2``) is then continued on the differential rotation-measure corrected and re-smoothed data (``smooth_corrected``).

Calibration of the Bandpass (bandpass)
--------------------------------------
The outcome of the re-calibration **after** correcting for the polarization alignment and Faraday rotation is loaded into **LoSoTo** in order to derive corrections for the bandpass. A robust flagging on the amplitude solutions as well as a Savitzky-Golay filter is applied in order to reject bad solutions and smooth the outcome. Frequency ranges up to a certain maximum width (``maxFlaggedWidth``) will be interpolated if flagged.
The following diagnostic plots are created:

- ``ampBFlag__??``: matrix plot of the amplitude solutions for the XX and YY polarization ``before`` flagging.
    .. image:: ampBFlag_polXX.png
- ``ampAFlag__??``: matrix plot of the amplitude solutions for the XX and YY polarization ``after`` flagging.
    .. image:: ampAFlag_polXX.png
- ``bandpass_pol??``: the derived bandpass of all stations in the XX and YY polarization.
    .. image:: bandpass_polXX.png
- ``bandpass_time??``: matrix plot of the derived bandpass, where both polarizations are color coded.
    .. image:: bandpass.png
- ``bandpass_time??_pol??``: plot of the derived bandpass of the XX and YY polarization, where all stations are color coded.
    .. image:: bandpass_polXX.png

The solutions are then stored in the final calibrator solution set ``cal_solutions`` and applied, together with the polarization alignment, the LOFAR beam correction and the Faraday rotation corrections to the interpolated data in the correct order (``apply_PA`` + ``apply_bandpass`` + ``apply_beam`` + ``apply_FR`` ).
The calibration (``calib_cal2``) is then continued on the bandpass-corrected and re-smoothed data (``smooth_corrected``).

Calibration of the instrumental (clock) and ionospheric delays (dTEC)
---------------------------------------------------------------------
The outcome of the re-calibration **after** correcting for the polarization alignment, the bandpass and the Faraday rotation is loaded into **LoSoTo** in order to derive corrections for the instrumental and ionospheric delays (ion). A robust flagging on the amplitude solutions is applied in order to reject bad solutions. These flags are applied to the phase solutions. These phase solutions should be mainly affected by instrumental (clock) and ionospheric (dTEC) delays. This **LoSoTo** step will aim for separating both effects (clock-dTEC separation).
The following diagnostic plots are created:

- ``ion_ampBFlag_pol??``: matrix plot of the amplitude solutions for the XX and YY polarization **before** flagging.
    .. image:: ion_ampBFlag_polXX.png
- ``ion_ampAFlag_pol??``: matrix plot of the amplitude solutions for the XX and YY polarization **after** flagging.
    .. image:: ion_ampAFlag_polXX.png
- ``ion_ph_pol??``: matrix plot of the phase solutions for the XX and YY polarization.
    .. image:: ion_ph_polXX.png
- ``ion_ph_poldif``: matrix plot of the phase solutions from XX-YY.
    .. image:: ion_ph_poldif.png
- ``clock``: matrix plot of the derived (instrumental) clock offsets in seconds.
    .. image:: clock.png
- ``tec``: matrix plot of the derived differential TEC in TECU.

    .. note::

        Some small jumps may be evident. These jump are due to splitting the solutions into multiple time chunks for processing (in which each chunk is treated independently) and simply represent the uncertainty with which the dTEC values can be derived (e.g., due to noise and 2-pi ambiguities in the phases used for fitting).

    .. image:: tec.png
- ``ion_ph-res_pol??``: matrix plot of the residual phase solutions for the XX and YY polarization after subtraction the derived instrumental and ionospheric delays. If the calibration went well, the residuals for all stations should be small. Any regions of large residuals will be flagged in the FLAGSTATION losoto step.
    .. image:: ion_ph-res_polXX.png
- ``ion_ph-res_poldif``: matrix plot of the residual phase solutions for XX-YY after subtraction of the derived instrumental and ionospheric delays.
    .. image:: ion_ph-res_poldif.png

The solutions are then stored in the final calibrator solution set ``cal_solutions``.

Feedback
--------
Lastly, metadata for the averaged, uncalibrated data and the final solutions are created so that the data products can be ingested into the LTA (``make_msfiles_metadata``).


User-defined parameter configuration
------------------------------------
**Parameters adjusted when specifying (via xmlgen.py or in MoM) the pipeline in the system**

*Information about the input data*

- ``cal_input_filenames``: specify the list of input MS filenames (full path).

*Information about the output*

- ``cal_output_filenames``: list of output MS filenames (full path).
- ``h5parm_output_filenames``: list of output solution table filenames (full path).

*Location of the software*

- ``prefactor_directory``: full path to the prefactor copy (default: ``$PREFACTOR_PATH``).

    .. note::

        On CEP-4, the ``PREFACTOR_PATH`` environment variable is set to the correct path when the Docker container is built.


**Parameters you may need to adjust**

*Data selection and calibration options*

- ``refant``: name of the station that will be used as a reference for the phase plotting, polarization alignment, Faraday rotation fitting, and clock/dTEC fitting steps.

    .. note::

        On CEP-4, this is set automatically to the first station in the first valid MS file that is not fully flagged.

- ``flag_baselines``: NDPPP-compatible pattern for baselines or stations to be flagged (default: ``[]``).
- ``process_baselines_cal``: performs A-Team-clipping/demixing only on these baselines (default: ``[CR]S*&``). Choose ``[CR]S*&`` if you want to process only cross-correlations and remove international stations.
- ``filter_baselines``: selects only this set of baselines to be processed (default: ``*``). Choose ``[CR]S*&`` if you want to process only cross-correlations and remove international stations.
- ``do_smooth``: enable or disable baseline-based smoothing (default: False). Enabling smoothing may enhance the SNR for LBA data but is not necessary for HBA data where the SNR is generally high.

    .. note::

        On CEP-4, this is set automatically to False for HBA data and True for LBA data.

- ``rfistrategy``: strategy to be applied with the statistical flagger (AOFlagger), default: ``HBAdefault.rfis``.

    .. note::

        On CEP-4, this is set automatically depending on the array type.

- ``max2interpolate``: amount of channels in which interpolation should be performed for deriving the bandpass (default: 30).
- ``interp_windowsize``: size of the window over which a value is interpolated (default: 15). Should be odd.
- ``raw_data``: use autoweight, set to True in case you are using raw data (default: False).
- ``ampRange``: range of median amplitudes accepted per station (default: ``[50,200]``).
- ``skip_international``: skip fitting the bandpass for international stations to avoid flagging them (default: True).
- ``propagatesolutions``: use already derived solutions as initial guess for the upcoming time slot if they converged (default: True).
- ``flagunconverged``: flag solutions for solves that did not converge if they were also detected to diverge (default: True).
- ``raw_data``: use autoweight, set to True in case you are using raw data (default: False).
- ``maxStddev``: maximum allowable standard deviation when outlier clipping is done (default: -1). For phases, this should value should be in radians, for amplitudes in log(amp). If None (or negative), a value of 0.1 rad is used for phases and 0.01 for amplitudes.

A comprehensive explanation of the baseline selection syntax can be found `here`_.


*Demixing options* (only used if demix step is added to the ``prep_cal_strategy`` variable)

- ``demix_sources``: choose sources to demix (provided as list), e.g., ``[CasA,CygA]``.
- ``demix_target``: if given, the target source model (its patch in the SourceDB) is taken into account when solving (default: ``""``).
- ``demix_freqstep``: number of channels to average when demixing (default: 16).
- ``demix_timestep`` : number of time slots to average when demixing (default: 10).

*Definition of pipeline options*

- ``cal_clocktec``: choose ``ct3,residuals3`` if you want to include 3rd order ionospheric effects during clock-dTEC separation (default: ``ct,residuals``). The inclusion of 3rd order effects may be useful when dealing with data at frequencies below 30 MHz.
- ``cal_ion``: choose whether you want to plot 1st or 3rd order ionospheric effects (default: ``{{ 1st_order }},smooth``). Add ``smooth`` if you want to use the median of the clock in time (suggested for HBA+LB). Do not use ``smooth`` for LBA data if the calibrator was observed simultaneously with the target as, in this case, one wants a time-dependent clock.

    .. note::

        On CEP-4, this is set automatically to ``{{ 1st_order }},smooth`` for HBA data and ``{{ 1st_order }}`` for LBA data.

- ``initial_flagging``: choose ``{{ raw_flagging }}`` if you process raw data (default: ``{{ default_flagging }}``).
- ``demix_step``: choose ``{{ demix }}`` if you want to demix (default: ``{{ none }}``).
- ``uvlambdamin``: minimum baseline length (in lambda) to include in solve. Stations with no valid baselines will be flagged in subsequent steps (default: 100).
- ``uvlambdamax``: maximum baseline length (in lambda) to include in solve. Stations with no valid baselines will be flagged in subsequent steps (default: 20000).
- ``tables2export``: comma-separated list of tables to export from the ionospheric calibration step (``cal_ion``) (default: ``clock``).

    .. note::

        On CEP-4, this is set automatically to ``clock`` for HBA data and ``phaseOrig`` for LBA data.


**Parameters for pipeline performance**

- ``error_tolerance``: defines whether pipeline run will continue if single bands fail (default: False).
- ``memoryperc``: maximum of memory used for aoflagger in ``raw_flagging`` mode in percent (default: 20).
- ``min_length``: minimum amount of subbands to concatenate in frequency necessary to perform the wide-band flagging in the RAM. If the data are too big aoflag will use indirect-read (default: 50).
- ``min_separation``: minimal accepted distance to an A-team source on the sky in degrees (default: 30). If one or more A-team sources is closer than this distance, a warning will be raised.

**Parameters you may want to adjust**

*Main directories*

- ``job_directory``: directory of the prefactor outputs (usually the ``job_directory`` as defined in the ``pipeline.cfg``, default: ``input.output.job_directory``).

*Script and plugin directories*

- ``scripts``: location of the prefactor scripts (default: ``{{ prefactor_directory }}/scripts``).
- ``pipeline.pluginpath``: location of the prefactor plugins: (default: ``{{ prefactor_directory }}/plugins``).

*Skymodel directory*

- ``calibrator_path_skymodel``: location of the prefactor sky models (default: ``{{ prefactor_directory }}/skymodels``).
- ``A-team_skymodel``: location of the A-team sky models (default: ``{{ calibrator_path_skymodel }}/Ateam_LBA_CC.skymodel``).

*Result directories*

- ``results_directory``: location of the prefactor results (default: ``{{ job_directory }}/results``).
- ``inspection_directory``: location of the inspection plots (default: ``{{ results_directory }}/inspection``).
- ``cal_values_directory``: directory of the calibration solutions (h5parm file, default: ``{{ results_directory }}/cal_values``).
- ``msfiles_metadata_file``: filename of output feedback metadata for MS files (no default).
- ``h5parm_metadata_file``: filename of output feedback metadata for the h5parm solutions file (no default).
- ``parset_prefix``: identifier for feedback (no default).

*Location of calibrator solutions*

- ``cal_solutions``: location of the calibration solutions (h5parm file, default: ``{{ cal_values_directory }}/cal_solutions.h5``).

*Averaging for the calibrator data*

- ``avg_timeresolution``: final time resolution of the data in seconds after averaging (default: 4).

    .. note::

        On CEP-4, this is set automatically to 4 for HBA data and 1 for LBA data.

- ``avg_freqresolution`` : final frequency resolution of the data after averaging (default: 48.82kHz, which translates to 4 channels per subband).

    .. note::

        The frequency resolution that can be used depends on the sampling clock frequency of the observation (160 or 200 MHz), as the
        number of channels after averaging must be a divisor of the total number of channels
        before averaging (per subband). On CEP-4, the value of ``avg_freqresolution`` is automatically adjusted to the closest
        valid value, depending on the sampling clock used in the observation.

- ``bandpass_freqresolution``: frequency resolution of the bandpass solution table (default: 195.3125kHz, which translates to 1 channel per subband).

    .. note::

        The frequency resolution that can be used depends on the sampling clock frequency of the observation (160 or 200 MHz), as the
        number of channels after averaging must be a divisor of the total number of channels
        before averaging (per subband). On CEP-4, the value of ``bandpass_freqresolution`` is automatically adjusted to the closest
        valid value, depending on the sampling clock used in the observation.


Parameters for **HBA** and **LBA** observations
-----------------------------------------------
====================== ========================== ==========================================
**parameter**          **HBA**                    **LBA**
---------------------- -------------------------- ------------------------------------------
``do_smooth``          ``False``                  ``True``
``rfistrategy``        ``HBAdefault.rifs``        ``LBAdefaultwideband.rfis``
``cal_clocktec``       ``ct,residuals``           ``ct,residuals`` or ``ct3,residuals3``
``cal_ion``            ``{{ 1st_order }},smooth`` ``{{ 1st_order }}`` or ``{{ 3rd_order }}``
``tables2export``      ``clock``                  ``phaseOrig``
``avg_timeresolution`` ``4``                      ``1``
``avg_freqresolution`` ``48.82kHz``               ``24.41kHz``
====================== ========================== ==========================================

In the case of **LBA** observations with frequencies below 30 MHz, you may want to use the 3rd-order dTEC fitting options above for ``cal_clocktec`` and ``cal_ion``. Otherwise, the default first-order fitting options should work well.

Differences between production and user versions
------------------------------------------------

The production version has the following primary differences relative to the user version:

    - input and output data must be specified as a list of filenames (instead of a directory+wildcard).
    - output solutions h5parm filename must be specified as a (typically length-one) list.
    - cluster-specific parameters (e.g., ``max_per_node`` or the paths to various executables such as the aoflagger) must be specified in the tasks
      configuration file (see the ``tasks.cfg`` file in the prefactor GitHub repository for a minimal example).
    - the ``PREFACTOR_PATH`` environment variable must be set to the prefactor installation directory.
    - the bandpass and clock-dTEC losoto steps are split over time chunks to
      allow them to run on multiple nodes simultaneously. The final phase residuals are
      calculated on each chunk separately, as the phase_offset resulting
      from the clock-dTEC step differs for each chunk.
    - feedback steps are done to generate and feed back metadata for the output data products (for
      ingest into the LTA).


.. _here: https://www.astron.nl/lofarwiki/doku.php?id=public:user_software:documentation:ndppp#description_of_baseline_selection_parameters
