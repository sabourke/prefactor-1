from lofarpipe.support.data_map import DataMap, DataProduct
import os
import multiprocessing


def find_flagged_antennas(ms_file):
    outputs = os.popen('DPPP msin=' + ms_file + ' msout=. steps=[count] count.type=counter count.warnperc=100 | grep NOTE').readlines()
    flaggedants = [ output.split('(')[-1].rstrip(')\n') for output in outputs ]
    return flaggedants


def plugin_main(args, **kwargs):
    """
    Takes in list of targets and an h5parm solution set and returns a list of stations
    in the target data which mismatch the calibrator solutions antenna table

    Parameters
    ----------
    mapfile_in : str
        Mapfile for input measurement sets
    filter: str
        Default filter constrains for the ndppp_prep_target step (usually removing International Baselines)

    Returns
    -------
    result : dict
        Output station names to filter
    """
    mapfile_in = kwargs['mapfile_in']
    filter = kwargs['filter']
    data = DataMap.load(mapfile_in)
    mslist = [item.file for item in data if not item.skip]
    if len(mslist) == 0:
        raise ValueError("Did not find any valid MS files in input mapfile!")

    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    flaggedants_list = pool.map(find_flagged_antennas, mslist)

    flagged_antenna_list = set.intersection(*map(set, flaggedants_list))

    for flagged_antenna in flagged_antenna_list:
        filter += ';!' + flagged_antenna + '*'

    print('Identified bad antennas: ' + str(flagged_antenna_list))

    result = {'filter': str(filter)}
    return result
