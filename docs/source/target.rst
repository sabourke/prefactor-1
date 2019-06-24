.. _target_pipeline:

Target pipeline
===============

This pipeline processes the target data in order to apply the direction-independent corrections from the calibrator pipeline. A first initial direction-independent self-calibration of the target field is performed, using a global sky model based on the `TGSS ADR`_ or the new Global Sky Model (GSM), and applied to the data.
You will find the single steps in the parameter ``pipeline.steps``.

This chapter will present the specific steps of the target pipeline in more detail.

All results (diagnostic plots and calibration solutions) are usually stored in a subfolder of the results directory, see ``inspection_directory`` and ``cal_values_directory``, respectively.

    .. note::

        In the following, example plots are shown for a well-behaved HBA calibration run. Results that differ significantly from these may indicate problems with the calibration and should be investigated in more detail if possible.


Prepare target
--------------
This part of the pipeline prepares the target data in order to be calibration-ready for the first direction-independent phase-only self-calibration against a global sky model.
These steps mainly includes mitigation of bad data (RFI, bad antennas, contaminations from A-Team sources), selection of the data to be calibrated (usually Dutch stations only), and some averaging to reduce data size and enhance the signal-to-noise ratio.
Furthermore, ionospheric Rotation Measure corrections are applied, using `RMextract`_
The pipeline must be run on pre-processed data only.

The basic steps are:

- mapping of data to be used (``target_input_filenames``).
- copying h5parm solution set from the calibrator (``copy_input_h5parmfile``).
- check of A-team relation to target: plot of the elevation of the target and A-team sources (plus the Sun, Jupiter, and the Moon) versus time (``check_Ateam_separation``).
    .. image:: A-Team_elevation_target.png
- gathering differential rotation measure (dRM) satellite information and writing it into the h5parm (``h5imp_RMextract``).
    .. image:: RMextract.png
- creating a model of A-Team sources to be subtracted (``make_sourcedb_ateam``).
- check for any missing solutions for the target data (``check_station_mismatch``).
- basic flagging and averaging (``ndppp_prep_target``).
    - edges of the band (``flagedge``) -- only used in ``raw_flagging`` mode.
    - statistical flagging (``aoflag``) -- only used in ``raw_flagging`` mode.
    - baseline flagging (``flag``).
    - low elevation flagging (below 20 degress elevation) (``elev``).
    - demix A-Team sources (``demix``) -- only used if specified.
    - applying clock offsets, polarization alignment, and bandpass correction derived from the calibrator (``applyclock``, ``applyPA``, ``applybandpass``).
    - applying LOFAR beam and Rotation Measure correction from `RMextract`_ (``applybeam``, ``applyRM``).
    - interpolation of flagged data (``interp``).
    - averaging of the data to 4 seconds and 4 channels per subband (``avg``).
- write A-Team sky model into the MODEL_DATA column (``predict_ateam``).
- clipping potentially A-Team affected data (``ateamcliptar``).
- interpolate, average (to 8 seconds and 2 channels per subband), and concatenate target data into chunks of ten subbands (``dpppconcat``). These chunks are enforced to be equidistant in frequency. Missing data will be filled back and flagged.
- wide-band statistical flagging (``aoflag``).

At the end of this stage, the data are prepared and cleaned of the majority of bad data. They are now ready for calibration.

Phase-only self-calibration
---------------------------
These steps aim for deriving a good first guess for the phase correction into the direction of the phase center (direction-independent phase correction).
Once this is done, the data are ready for further processing with direction-dependent calibration techniques, using software like `factor`_ or `killMS`_ or other
generic pipelines (e.g., to exploit the content of the long-baseline data).

- download global sky model for the target field automatically (``sky_tar``).
- interpolate flagged data and perform direction-independent phase-only calibration (diagonal terms) within a limited baseline range (by default, baselines for the core and remote stations only), using the filter (``gsmcal``).
- remove chunks with more than the given threshold fraction of flagged data (``check_unflagged``).
- identify fully flagged antennas (``check_bad_antennas``).
- apply the direction-independent phase-only calibration solutions and average to the values set by ``avg_freqresolution_concat`` and ``avg_timeresolution_concat`` (``apply_phase`` or ``apply_tec``).

All solutions are stored in the h5parm file format.
The apply step also incorporates full `Dysco`_ compression to save disk space. The fully calibrated data are stored in the DATA column.

The phase solutions derived from the preparation step are collected and loaded into **LoSoTo** to provide diagnostic plots:

- ``ph_freq??``: matrix plot of the phase solutions with time for a particular chunk of target data, where both polarizations are colorcoded.
    .. image:: ph_freq.png
- ``ph_poldif_freq??``: matrix plot of the XX-YY phase solutions with time for a particular chunk of target data.
    .. image:: ph_poldif_freq.png
- ``ph_pol??``: matrix plot of the phase solutions for the XX and YY polarization.
    .. image:: ph_polXX.png
- ``ph_poldif``: matrix plot of the phase solutions for the XX-YY polarization.
    .. image:: ph_poldif.png

Feedback
--------
Lastly, metadata for the averaged, calibrated data and the final solutions are created so that the data products can be ingested into the LTA (``make_msfiles_metadata``).


User-defined parameter configuration
------------------------------------
**Parameters adjusted when specifying (via xmlgen.py or in MoM) the pipeline in the system**

*Information about the input data*

- ``target_input_filenames``: list of input MS filenames (full path).
- ``h5parm_input_filename``: filename of the input calibration solutions h5parm file (from the calibrator pipeline).

*Information about the output data*

- ``target_output_filenames``: list of output MS filenames (full path).

*Location of the software*

- ``prefactor_directory``: full path to your prefactor copy.

    .. note::

        On CEP-4, the ``PREFACTOR_PATH`` environment variable must be set to the prefactor installation directory (which is inside the Docker container).


**Parameters you may need to adjust**

*Data selection and calibration options*

- ``refant``: name of the station that will be used as a reference for the phase plotting.

    .. note::

        On CEP-4, this is set automatically to the first station in the first valid MS file that is not fully flagged.

- ``flag_baselines``: NDPPP-compatible pattern for baselines or stations to be flagged (default: ``[]``).
- ``filter_baselines``: selects only this set of baselines to be processed (default: ``[CR]S*&``). Choose ``[CR]S*&`` if you want to process only cross-correlations and remove international stations.
- ``do_smooth``: enable or disable baseline-based smoothing (default: ``False``). Enabling smoothing may enhance the SNR for LBA data but is not necessary for HBA data where the SNR is generally high.

    .. note::

        On CEP-4, this is set automatically to ``False`` for HBA data and ``True`` for LBA data.

- ``rfistrategy``: strategy to be applied with the statistical flagger (AOFlagger), default: ``HBAdefault.rfis``.

    .. note::

        On CEP-4, this is set automatically depending on the array type.

- ``interp_windowsize``: size of the window over which a value is interpolated. Should be odd. (default: ``15``).
- ``raw_data``: use autoweight, set to True in case you are using raw data (default: ``False``).
- ``min_unflagged_fraction``: minimal fraction of unflagged data to be accepted for further processing of the data chunk (default: ``0``).
- ``compression_bitrate``: defines the bitrate of Dysco compression of the data after the final step, choose ``0`` if you do NOT want to compress the data (default: ``16``).
- ``propagatesolutions``: use already derived solutions as initial guess for the upcoming time slot (default: ``True``).

A comprehensive explanation of the baseline selection syntax can be found `here`_.

*Demixing options* (only used if demix step is added to the ``prep_targ_strategy`` variable)

- ``demix_sources``: choose sources to demix (provided as list), e.g., ``[CasA,CygA]``
- ``demix_target``: if given, the target source model (its patch in the SourceDB) is taken into account when solving (default: ``""``)
- ``demix_freqstep``: number of channels to average when demixing (default: ``16``)
- ``demix_timestep`` : number of time slots to average when demixing (default: ``10``)

*Definitions for pipeline options*

- ``initial_flagging``: choose ``{{ raw_flagging }}`` if you process raw data (default: ``{{ default_flagging }}``).
- ``demix_step``: choose ``{{ demix }}`` if you want to demix (default: ``{{ none }}``).
- ``apply_steps``:  comma-separated list of apply_steps performed in the target preparation (default: ``applyclock,applybeam,applyRM``). Note: only use ``applyRM`` if you have performed the RMextract step before.

    .. note::

        On CEP-4, this is set automatically to ``applyclock,applybeam,applyRM`` for HBA data and ``applyphase`` for LBA data.

- ``clipAteam_step``:  choose ``{{ none }}`` if you want to skip A-team-clipping, e.g. when demixing has been done (default: ``{{ clipATeam }}``).
- ``gsmcal_step``:  choose ``tec`` if you want to fit dTEC instead of self-calibrating for phases (default: ``phase``).

    .. note::

        On CEP-4, this is set automatically to ``phase`` for HBA data and ``tec`` for LBA data.

- ``updateweights``:  update the weights column, in a way consistent with the weights being inverse proportional to the autocorrelations (default: True).


**Parameters for pipeline performance**

- ``error_tolerance``: defines whether pipeline run will continue if single bands fail (default: ``False``).
- ``min_length``: defines the minimum amount of subbands to concatenate in frequency necessary to perform the wide-band flagging in the RAM (default: ``50``). If the data are too large, aoflagger will use indirect read.
- ``min_separation``: minimal accepted distance to an A-team source on the sky in degrees (default: ``30``). If one or more A-team sources is closer than this distance, a warning will be raised.

**Parameters you may want to adjust**

*Main directories*

- ``job_directory``: directory of the prefactor outputs (usually the ``job_directory`` as defined in the ``pipeline.cfg``, default: ``input.output.job_directory``).

*Script and plugin directories*

- ``scripts``: location of the prefactor scripts (default: ``{{ prefactor_directory }}/scripts``).
- ``pipeline.pluginpath``: location of the prefactor plugins: (default: ``{{ prefactor_directory }}/plugins``).

*Skymodel directory*

- ``target_skymodel``: location of the target sky model or filename in which it will be stored (default: ``{{ job_directory }}/target.skymodel``), use False for ``use_tgss_target`` in case ``target_skymodel`` is already a pre-existing user-supplied skymodel.
- ``use_tgss_target``: download the phase-only calibration sky model from TGSS or GSM (``Force`` : always download , ``True`` download if ``{{ target_skymodel }}`` does not exist , ``False`` : never download).
- ``skymodel_source``: Source of the sky model used for calibration of the field: ``TGSS`` or ``GSM`` (default: ``TGSS``).

    .. note::

        On CEP-4, this is set automatically to ``TGSS`` for HBA data and to ``GSM`` for LBA data.

- ``calibrator_path_skymodel``: location of the sky models (default: ``{{ prefactor_directory }}/skymodels``).
- ``A-team_skymodel``: location of the A-team sky models (default: ``{{ calibrator_path_skymodel }}/Ateam_LBA_CC.skymodel``).
- ``target_skymodel``:  path to the sky model for the phase-only calibration of the target (default: ``{{ job_directory }}/target.skymodel``). Note: all sources should be in a single patch.
- ``use_target``:  download the phase-only calibration sky model from TGSS, ``Force``: always download , ``True``: download if ``{{ target_skymodel }}`` does not exist , ``False``: never download (default: ``True``).

*Result directories*

- ``results_directory``: location of the prefactor results (default: ``{{ job_directory }}/results``).
- ``inspection_directory``: location of the inspection plots (default: ``{{ results_directory }}/inspection``).
- ``cal_values_directory``: directory of the calibration solutions (h5parm file, default: ``{{ results_directory }}/cal_values``).
- ``msfiles_metadata_file``: filename of output feedback metadata for MS files (no default).
- ``h5parm_metadata_file``: filename of output feedback metadata for the h5parm solutions file (no default).
- ``parset_prefix``: identifier for feedback (no default).

*Location of calibrator solutions*

- ``cal_solutions``: location of the calibration solutions (h5parm file, default: ``{{ cal_values_directory }}/cal_solutions.h5``).

*Averaging for the target data*

- ``avg_timeresolution``: intermediate time resolution of the data in seconds after averaging (default: ``4``).
- ``avg_freqresolution`` : intermediate frequency resolution of the data after averaging (default: ``48.82kHz``, which translates to 4 channels per subband for the 200 MHz sampling clock).

    .. note::

        The frequency resolution that can be used depends on the sampling clock frequency of the observation (160 or 200 MHz), as the
        number of channels after averaging must be a divisor of the total number of channels
        before averaging (per subband). On CEP-4, the value of ``avg_freqresolution`` is automatically adjusted to the closest
        valid value, depending on the sampling clock used in the observation.

- ``avg_timeresolution_concat``: final time resolution of the data in seconds after averaging and concatenation (default: ``8``).
- ``avg_freqresolution_concat``: final frequency resolution of the data after averaging and concatenation (default: ``97.64kHz``, which translates to 2 channels per subband for the 200 MHz sampling clock).

    .. note::

        The frequency resolution that can be used depends on the sampling clock frequency of the observation (160 or 200 MHz), as the
        number of channels after averaging must be a divisor of the total number of channels
        before averaging (per subband). On CEP-4, the value of ``avg_freqresolution_concat`` is automatically adjusted to the closest
        valid value, depending on the sampling clock used in the observation.


*Concatenating of the target data*

- ``num_SBs_per_group``: make concatenated measurement-sets with that many subbands (default: ``10``). Set to a negative value to concatenate all subbands.
- ``reference_stationSB``: station-subband number to use as reference for grouping, (default: ``None`` -> use lowest frequency input data as reference).

*RMextract settings*

- ``ionex_server``: URL of the *IONEX* server (default: "ftp://ftp.aiub.unibe.ch/CODE/").
- ``ionex_prefix``: the prefix of the *IONEX* files (default: ``CODG``).
- ``ionex_path``: location of the *IONEX* files after downloading (default: ``{{ job_directory }}/IONEX/``).

Parameters for **HBA** and **LBA** observations
-----------------------------------------------
================================ ====================== ===========================
**parameter**                    **HBA**                **LBA**
-------------------------------- ---------------------- ---------------------------
``do_smooth``                    ``False``              ``True``
``rfistrategy``                  ``HBAdefault.rfis``    ``LBAdefaultwideband.rfis``
``apply_steps``                  ``applyclock,applyRM`` ``applyphase``
``gsmcal_step``                  ``phase``              ``tec``
``skymodel_source``              ``TGSS``               ``GSM``
``clipATeam_step``               ``{{ clipATeam }}``    ``{{ none }}``
``avg_timeresolution``           ``4.0``                ``1.0``
``avg_freqresolution``           ``48.82kHz``           ``48.82kHz``
``avg_timeresolution_concat``    ``8.0``                ``4.0``
``avg_freqresolution_concat``    ``97.64kHz``           ``48.82kHz``
``num_SBs_per_group``            ``10``                 ``-1``
================================ ====================== ===========================

In the case of **LBA** observations, by default the full phase solutions from the calibrator are applied, as it is assumed that the calibrator is observed simultaneously with the target.
Additionally, if your **LBA** data have **not** been demixed you may still want to keep the A-Team-clipping.


Differences between production and user versions
------------------------------------------------

The production version has the following primary differences relative to the user version:

    - input and output data must be specified as a list of filenames (instead of a directory+wildcard).
    - output solutions h5parm filename must be specified as a (typically length-one) list.
    - cluster-specific parameters (e.g., ``max_per_node`` or the paths to various executables such as the aoflagger) must be specified in the tasks.
      configuration file (see the ``tasks.cfg`` file in the prefactor GitHub repository for a minimal example).
    - the ``PREFACTOR_PATH`` environment variable must be set to the prefactor installation directory.
    - target solutions are applied to the individual subbands rather than to the concatenated ones (to
      preserve the one-to-one mapping between input and output).
    - feedback steps are done to generate and feed back metadata for the output data products (for
      ingest into the LTA).

.. _RMextract: https://github.com/lofar-astron/RMextract/
.. _factor: https://github.com/lofar-astron/factor/
.. _killMS: https://github.com/saopicc/killMS/
.. _TGSS ADR: https://http://tgssadr.strw.leidenuniv.nl/
.. _Dysco: https://github.com/aroffringa/dysco/
.. _here: https://www.astron.nl/lofarwiki/doku.php?id=public:user_software:documentation:ndppp#description_of_baseline_selection_parameters
