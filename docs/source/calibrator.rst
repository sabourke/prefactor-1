.. _calibrator_pipeline:

Calibrator pipeline
===================

This pipeline processes the calibrator data in order to derive direction-independent corrections.
It will take into account the correct order of distortions to be calibrated for.
This chapter will present the specific steps of the calibrator pipeline in more detail.
You will find the single steps in the parameter ``pipeline.steps``.
All results (diagnostic plots and calibration solutions) are usually stored in a subfolder of the results directory, see ``inspection_directory`` and ``cal_values_directory``, respectively.

    .. image:: calibscheme.png

Prepare calibrator (incl. "demixing")
-------------------------------------

This part of the pipeline prepares the calibrator data in order to be calibration-ready.
This mainly includes mitigation of bad data (RFI, bad antennas, contaminations from A-Team sources), selection of the data to be calibrated (usually Dutch stations only), and some averaging to reduce data size and enhance the signal-to-noise ratio.
The user can specify whether to do raw data or pre-processed data flagging and whether demixing should be performed.

The basic steps are:

- mapping of data to be used (``cal_input_filenames``)
- creating a model of A-Team sources to be subtracted (``make_sourcedb_ateam``)
- basic flagging and averaging (``ndppp_prep_cal``)
    - edges of the band (``flagedge``) -- only used in ``raw_flagging`` mode
    - statistical flagging (``aoflag``) -- only used in ``raw_flagging`` mode
    - baseline flagging (``flag``)
    - low elevation flagging (below 20 degress elevation) (``elev``)
    - demix A-Team sources (``demix``) -- only used if specified
    - interpolation of flagged data (``interp``)
    - averaging of the data to 4 sec and 4 channels per subband (``avg``)
- wide-band statistical flagging (``aoflag``)
- find needed skymodel of calibrator automatically (``sky_cal``)
- write the calibrator skymodel into the MODEL_DATA column (``predict_cal``)
- interpolate flagged data from the wide-band statistical flagging step (``interp_cal``)
- baseline-dependent smoothing of the data (``smooth_data``)
- perform direction-independent phase-only calibration (diagonal terms + common rotation angle) (``calib_cal``)
- feed back results so that they can be ingested into the LTA (``make_msfiles_metadata``)

The solutions are stored in the h5parm file format.

Calibration of the polarization alignment (PA)
----------------------------------------------
The phase solutions derived from the preparation step are now collected and loaded into **LoSoTo**.
**LoSoTo** will derive the polarizion alignment and provide diagnostic plots:

- ``polalign_ph_pol??``: matrix plot of the phase solutions for the XX and YY polarization
    .. image:: polalign_ph_polXX.png
- ``polalign_ph_poldif``: matrix plot of the phase solutions from XX-YY
    .. image:: polalign_ph_poldif.png
- ``polalign_rotange``: matrix plot of the common rotation angle solutions
    .. image:: polalign_rotangle.png
- ``polalign_amp_pol??``: matrix plot of the amplitude solutions for the XX and YY polarization
    .. image:: polalign_amp_polXX.png
- ``polalign``: matrix plot of the derived polarization alignment between XX and YY
    .. image:: polalign.png
- ``polalign_ph-res_pol??``: matrix plot of the residual phase solutions for the XX and YY polarization after subtraction the derived polarization alignment
- ``polalign_ph-res_poldif``: matrix plot of the residual phase solutions for XX-YY after subtraction of the derived polarization alignment

The solutions are then stored in the final calibrator solution set ``cal_solutions`` (line 83) and applied to the interpolated data (``apply_PA``), together with the LOFAR beam correction (``apply_beam``)
The calibration (``calib_cal``) is then repeated on the corrected and re-smoothed data (``smooth_corrected``).

Calibration of the Faraday Rotation (FR)
----------------------------------------
The outcome of the re-calibration **after** correcting for the polarization alignment is again loaded into **LoSoTo** in order to derive corrections for Faraday Rotation.
The following diagnostic plots are created:

- ``fr_ph_pol??``: matrix plot of the phase solutions for the XX and YY polarization
- ``fr_ph_poldif``: matrix plot of the phase solutions from XX-YY
- ``fr_rotange``: matrix plot of the common rotation angle solutions
- ``fr_amp_pol??``: matrix plot of the amplitude solutions for the XX and YY polarization
- ``fr``: matrix plot of the derived differential Rotation Measure from Faraday Rotation
    .. image:: fr.png
- ``fr_ph-res_pol??``: matrix plot of the residual phase solutions for the XX and YY polarization after subtraction the derived Rotation Measure
- ``fr_ph-res_poldif``: matrix plot of the residual phase solutions for XX-YY after subtraction of the derived Rotation Measure

The solutions are then stored in the final calibrator solution set ``cal_solutions`` (line 83) and applied, together with the polarization alignment and the LOFAR beam correction, to the interpolated data (``apply_PA`` + ``apply_beam`` + ``apply_FR``).
The calibration (``calib_cal``) is then repeated on the corrected and re-smoothed data (``smooth_corrected``).

Calibration of the Bandpass (bandpass)
----------------------------------------
The outcome of the re-calibration **after** correcting for the polarization alignment and Faraday Rotation is loaded into **LoSoTo** in order to derive corrections for the bandpass. A robust flagging on the amplitude solutions as well as a Savitzky-Golay filter is applied in order to reject bad solutions and smooth the outcome. Frequency regimes up to a certain maximum width (``maxFlaggedWidth``) will be interpolated if flagged.
The following diagnostic plots are created:

- ``ampBFlag__??``: matrix plot of the amplitude solutions for the XX and YY polarization ``before`` flagging
    .. image:: ampBFlag_polXX.png
- ``ampAFlag__??``: matrix plot of the amplitude solutions for the XX and YY polarization ``after`` flagging
    .. image:: ampAFlag_polXX.png
- ``bandpass_pol??``: the derived bandpass of all stations in the XX and YY polarization
- ``bandpass_time??``: matrix plot of the derived bandpass, where both polarizations are colorcoded
    .. image:: bandpass.png
- ``bandpass_time??_pol??``: plot of the derived bandpass of the XX and YY polarization, where all stations are colorcoded
    .. image:: bandpass_polXX.png

The solutions are then stored in the final calibrator solution set ``cal_solutions`` (line 83) and applied, together with the polarization alignment, the LOFAR beam correction and the Faraday Rotation corrections to the interpolated data in the correct order (``apply_PA`` + ``apply_bandpass`` + ``apply_beam`` + ``apply_FR`` ).
The calibration (``calib_cal``) is then repeated on the corrected and re-smoothed data (``smooth_corrected``).

Calibration of the instrumental and ionospheric delays (ion)
------------------------------------------------------------
The outcome of the re-calibration **after** correcting for the polarization alignment, the bandpass and the Faraday Rotation is loaded into **LoSoTo** in order to derive corrections for the instrumental and ionospheric delays. A robust flagging on the amplitude solutions is applied in order to reject bad solutions. These flags are applied to the phase solutions. These phase solutions should be mainly affected by instrumental (clock) and ionospheric (TEC) delays. This **LoSoTo** step will aim for seperating both effects (clock-TEC separation).
The following diagnostic plots are created:

- ``ion_ampBFlag__??``: matrix plot of the amplitude solutions for the XX and YY polarization **before** flagging
- ``ion_ampAFlag__??``: matrix plot of the amplitude solutions for the XX and YY polarization **after** flagging
- ``ion_ph_pol??``: matrix plot of the phase solutions for the XX and YY polarization
- ``ion_ph_poldif``: matrix plot of the phase solutions from XX-YY
- ``clock``: matrix plot of the derived (instrumental) clock offsets in seconds
    .. image:: clock.png
- ``tec``: matrix plot of the derived differential TEC in TECU
    .. image:: tec.png
- ``ion_ph-res_pol??``: matrix plot of the residual phase solutions for the XX and YY polarization after subtraction the derived instrumental and ionospheric delays
- ``ion_ph-res_poldif``: matrix plot of the residual phase solutions for XX-YY after subtraction of the derived instrumental and ionospheric delays
    .. image:: ion_ph-res_poldif.png

The solutions are then stored in the final calibrator solution set ``cal_solutions`` (line 83).

User-defined parameter configuration
------------------------------------
**Parameters you will need to adjust**

*Information about the input data*

- ``cal_input_filenames``: specify the list of input MS filenames (full path)

*Information about the output*

- ``cal_output_filenames``: list of output MS filenames (full path)
- ``h5parm_output_filenames``: list of output solution table filenames (full path)

*Location of the software*

- ``prefactor_directory``: full path to your prefactor copy


**Parameters you may need to adjust**

*Data selection and calibration options*

- ``refant``: name of the station that will be used as a reference for the phase-plots
- ``flag_baselines``: NDPPP-compatible pattern for baselines or stations to be flagged (may be an empty list, i.e.: ``[]`` )
- ``filter_baselines``: selects only this set of baselines to be processed. Choose [CR]S*& if you want to process only cross-correlations and remove international stations.
- ``do_smooth``: enable or disable baseline-based smoothing
- ``rfistrategy``: strategy to be applied with the statistical flagger (AOFlagger), default: ``HBAdefault.rfis``
- ``max2interpolate``: amount of channels in which interpolation should be performed for deriving the bandpass (default: 30)
- ``interp_windowsize``: size of the window over which a value is interpolated. Should be odd. (default: 15)
- ``raw_data``: use autoweight, set to True in case you are using raw data (default: False)
- ``ampRange``: range of median amplitudes accepted per station
- ``skip_international``: skip fitting the bandpass for international stations (this avoids flagging them in many cases)
- ``propagatesolutions``: use already derived solutions as initial guess for the upcoming time slot (if they converged)
- ``flagunconverged``: flag solutions for solves that did not converge (if they were also detected to diverge)
- ``maxStddev``: maximum allowable standard deviation when outlier clipping is done. For phases, this should value should be in radians, for amplitudes in log(amp). If None (or negative), a value of 0.1 rad is used for phases and 0.01 for amplitudes

A comprehensive explanation of the baseline selection syntax can be found `here`_.


*Demixing options* (only used if demix step is added to the ``prep_cal_strategy`` variable)

- ``demix_sources``: choose sources to demix (provided as list), e.g., ``[CasA,CygA]``
- ``demix_target``: if given, the target source model (its patch in the SourceDB) is taken into account when solving (default: ``""``)
- ``demix_freqstep``: number of channels to average when demixing (default: 16)
- ``demix_timestep`` : number of time slots to average when demixing (default: 10)

*Definitions for pipeline options*

- ``cal_clocktec``: choose ``ct3`` if you want to include 3rd order ionospheric effects during clock-TEC separation (default: ``ct``)
- ``cal_ion``: choose whether you want to plot 1st or 3rd order ionospheric effects (default: ``{{ 1st_order }}``)
- ``initial_flagging``: choose ``{{ raw_flagging }}`` if you process raw data
- ``demix_step``: choose ``{{ demix }}`` if you want to demix
- ``tables2export``: comma-separated list of tables to export from the ionospheric calibration step (``cal_ion``)


**Parameters for pipeline performance**

- ``error_tolerance``: defines whether pipeline run will continue if single bands fail (default: False)
- ``memoryperc``: maximum of memory used for aoflagger in ``raw_flagging`` mode in percent
- ``min_length``: minimum amount of subbands to concatenate in frequency necessary to perform the wide-band flagging in the RAM. It data is too big aoflag will use indirect-read.
- ``min_separation``: minimal accepted distance to an A-team source on the sky in degrees (will raise a WARNING)

**Parameters you may want to adjust**

*Main directories*

- ``job_directory``: directory of the prefactor outputs (usually the ``job_directory`` as defined in the ``pipeline.cfg``, default: ``input.output.job_directory``)

*Script and plugin directories*

- ``scripts``: location of the prefactor scripts (default: ``{{ prefactor_directory }}/scripts``)
- ``pipeline.pluginpath``: location of the prefactor plugins: (default: ``{{ prefactor_directory }}/plugins``)

*Skymodel directory*

- ``calibrator_path_skymodel``: location of the prefactor skymodels (default: ``{{ prefactor_directory }}/skymodels``)
- ``A-team_skymodel``: location of the A-team skymodels (default: ``{{ calibrator_path_skymodel }}/Ateam_LBA_CC.skymodel``)

*Result directories*

- ``results_directory``: location of the prefactor results (default: ``{{ job_directory }}/results``)
- ``inspection_directory``: location of the inspection plots (default: ``{{ results_directory }}/inspection``)
- ``cal_values_directory``: directory of the calibration solutions (h5parm file, default: ``{{ results_directory }}/cal_values``)
- ``msfiles_metadata_file``: filename of output feedback metadata for MS files
- ``h5parm_metadata_file``: filename of output feedback metadata for the h5parm solutions file
- ``parset_prefix``: identifier for feedback

*Location of calibrator solutions*

- ``cal_solutions``: location of the calibration solutions (h5parm file, default: ``{{ cal_values_directory }}/cal_solutions.h5``)

*Averaging for the calibrator data*

- ``avg_timeresolution``: final time resolution of the data in seconds after averaging (default: 4)
- ``avg_freqresolution`` : final frequency resolution of the data after averaging (default: 48.82kHz, which translates to 4 channels per subband)
- ``bandpass_freqresolution``: frequency resolution of the bandpass solution table (default: 195.3125kHz, which translates to 1 channel per subband)

Parameters for **HBA** and **LBA** observations
-----------------------------------------------
====================== =============== =======================
**parameter**          **HBA**         **LBA**
---------------------- --------------- -----------------------
``do_smooth``          False           True
``rfistrategy``        HBAdefault.rifs LBAdefaultwideband.rfis
``cal_clock``          ct              ct3
``cal_ion``            {{ 1st_order }} {{ 3rd_order }}
``tables2export``      clock           phaseOrig
``avg_timeresolution`` 4               1
====================== =============== =======================

In case of **LBA** observation you might also want to enable demixing in the ``prep_cal_strategy`` variable.

Differences between production and user versions
------------------------------------------------

The production version has the following primary differences relative to the user version:

    - input and output data must be specified as a list of filenames (instead of a directory+wildcard)
    - output solutions h5parm filename must be specified as a (typically length-one) list
    - cluster-specific parameters (e.g., ``max_per_node`` or the paths to various executables such as the aoflagger) must be specified in the tasks
      configuration file (see the ``tasks.cfg`` file in the prefactor GitHub repository for a minimal example)
    - the PREFACTOR_PATH environment variable must be set to the prefactor installation directory
    - the bandpass and clock-TEC losoto steps are split over time chunks to allow them to run on multiple nodes simultaneously
    - feedback steps are done to generate and feed back metadata for the output data products (for
      ingest into the LTA)


.. _here: https://www.astron.nl/lofarwiki/doku.php?id=public:user_software:documentation:ndppp#description_of_baseline_selection_parameters
