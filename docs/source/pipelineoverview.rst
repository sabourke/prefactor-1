.. _pipeline_overview:

Pipeline overview
=================

Prefactor contains pipeline parsets for the tasks needed to prepare the data for facet calibration:

``Pre-Facet-Calibrator``
    Processes the (amplitude-)calibrator to derive direction-independent corrections. See :ref:`calibrator_pipeline` for details.
``Pre-Facet-Target``
    Transfers the direction-independent corrections to the target and does direction-independent calibration of the target using core and remote stations only. See :ref:`target_pipeline` for details.
``Pre-Facet-Image``
    Images the full FoV. See :ref:`image_pipeline` for details.


CEP-4-Specific Information
--------------------------

The following information applies to production runs done on the CEP-4 cluster. In the following, the SAS ID of the pipeline (e.g., 698995) is designated with "XXXXXX".

**Data flow**
    The data flow adopted on CEP-4 is as follows:

    * **Preprocessing pipeline**: the raw calibrator and target data are flagged, demixed (if needed), and averaged. The output data products are then Dysco-compressed and ingested for storage on the LTA.
    * **Calibrator pipeline**: the ``Pre-Facet-Calibrator`` pipeline is run on the preprocessed data and the output data products (Dysco-compressed, averaged data and solution tables) are ingested.
    * **Target pipeline**: the ``Pre-Facet-Target`` pipeline is run on the preprocessed data and the output data products (Dysco-compressed, averaged data and solution tables) are ingested.
    * **Image pipeline**: the ``Pre-Facet-Image`` pipeline is run on the output data of the target pipeline and the output image is ingested.

    .. note::

        In the calibrator and target pipelines, Dysco compression is used for a second time (the first being done during the preprocessing pipeline). Tests have that shown this second compression adds a negligible amount of noise to the data.
**Pipeline config files**
    The pipeline configuration files are located inside the Docker container at ``/opt/lofar/share/pipeline``.
**Parset**
    The prefactor parset is located at ``/data/parsets/ObservationXXXXXX.parset_prefactor``.
**Output data products**
    The output MS files, etc. are located at ``/data/projects/PROJECT_NAME/LXXXXXX``.
**Inspection plots**
    The inspection plots are located in ``/data/scratch/ObservationXXXXXX/results/inspection``. These plots can be viewed at the LOFAR QA webpage at http://head01.cep4.control.lofar:8521/pipeline_plots/XXXXXX.
**Pipeline log**
    The log of the pipeline run is located at ``/data/log/pipeline-XXXXXX-XXXX.log``.



