.. _image_pipeline:

Image pipeline
==============

This pipeline produces an image of the full FOV of the target data, using the full bandwidth. The
parset is named ``Pre-Facet-Image.parset``.


Prepare target
--------------

The target data that result from the target pipeline are averaged and concatenated in preparation for imaging. The steps
are as follows:

``create_ms_map``
    Generate a mapfile of all the target data. The files must be supplied as a
    list of the full paths to the files.
``combine_mapfile``
    Generate a mapfile with all files in a single entry. This mapfile is used as
    input to the next step.
``do_magic``
    Compute image sizes and the number of channels to use during imaging from the MS
    files from the previous step. The image size is calculated from the FWHM of the
    primary beam at the lowest frequency at the mean elevation of the observation. The
    number of channels is set simply as the number of subbands / 40, to result in
    enough channels to allow multi-frequency synthesis (MFS), but not so many that
    performance is impacted. A minimum of 2 channels is used.
``do_magic_maps``
    Convert the output of do_magic into usable mapfiles.
``average``
    Average the data as appropriate for imaging of the FOV. The amount of averaging
    depends on the size of the image (to limit bandwidth and time smearing). The
    averaging currently adopted is 16 s per time slot and 0.2 MHz per channel. These
    values result in low levels of bandwidth and time smearing for the target image
    sizes and resolutions.
``combine_mapfile_deep``
    Generate a mapfile with all files in a single entry. This mapfile is used as
    input to the next step.
``dpppconcat``
    Run DPPP to concatenate the data. Concatenating the data speeds up gridding
    and degridding with IDG by factors of several.


Imaging
-------
WSClean is used to produce the image. See the parset and the ``do_magic`` step above
for details of the parameters used. They are chosen to produce good results for most
standard observations.

``wsclean_high_deep``
    Image the data with WSClean+IDG. Imaging is done in MFS mode, resulting in a
    single image for the full bandwidth. A typical HBA Stokes-I image looks like the one below.

    .. image:: image_pipeline_example.png
``plot_im_high``
    Make a png figure of the image, including estimates of the image rms and dynamic
    range and the restoring beam size.
``make_source_list``
    Make a list of sources from the image using PyBDSF and compare their properties to
    those of the GSM catalog.
``copy_output_images``
    Copy the image to the output filenames expected for feedback.
``make_image_metadata``
    Make feedback metadata for the output image. This step is needed to make the
    info needed for ingest into the LTA. This info includes the RA, Dec of the image
    center, an estimate of the image rms noise, the frequency, etc.


User-defined parameter configuration
------------------------------------
- ``data_input_filenames``
    List of input MS filenames (full path).
- ``image_output_filenames``
    List of output image filenames for feedback (full path).
- ``cellsize_highres_deg``
    Cellsize in degrees.
- ``fieldsize_highres``
    Size of the image is this value times the FWHM of mean semi-major axis of
    the station beam at the lowest observed frequency.
- ``maxlambda_highres``
    Maximum uv-distance in lambda that will be used for imaging.
- ``image_padding``
    How much padding shall we add during the imaging?
- ``idg_mode``
    IDG mode to use: cpu or hybrid (= CPU + GPU).
- ``local_scratch_dir``
    Scratch directory for WSClean (can be local to the processing nodes!).
- ``images_metadata_file``
    Feedback metadata file (full path).
- ``parset_prefix``
    Feedback parset prefix.
- ``image_rootname``
    Output image root name. The image will be named ``image_rootname-MFS-image.fits``.


Parameters for **HBA** and **LBA** observations
-----------------------------------------------
======================== ================== =======================
**parameter**            **HBA**            **LBA**
------------------------ ------------------ -----------------------
``cellsize_highres_deg``   0.00208              0.00416
======================== ================== =======================


Differences between production and user versions
------------------------------------------------

The imaging pipeline is only available on the production branch.
