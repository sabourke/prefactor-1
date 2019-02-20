from lofarpipe.support.data_map import DataMap
import casacore.tables as ct


def plugin_main(args, **kwargs):
    """
    Finds target name for observation

    Parameters
    ----------
    mapfile_in : str
        Mapfile for input measurement sets

    Returns
    -------
    result : dict
        Output name
    """
    mapfile_in = kwargs['mapfile_in']
    data = DataMap.load(mapfile_in)
    msfile = data[0].file

    observationTable = ct.table(msfile+'::OBSERVATION')
    targetName = observationTable.getcol('LOFAR_TARGET')['array'][0]
    result = {'targetName': targetName}

    return result
