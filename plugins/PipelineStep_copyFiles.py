import os
import shutil
from lofarpipe.support.data_map import DataMap, DataProduct
from lofarpipe.support.utilities import delete_directory


def plugin_main(args, **kwargs):
    """
    Copies single file in mapfile to list of files

    Parameters
    ----------
    input_mapfile: str
        Filename of input mapfile with file that is to be copied. Either this or
        input_file must be specified
    input_file : str
        Filename of input file that is to be copied. Either this or
        input_mapfile must be specified
    output_files : list or str
        List of files or mapfile with such a list as the only entry. May be
        given as a list of strings or as a string (e.g.,
        '[s1.skymodel, s2.skymodel]'
    hosts : list or str
        List of hosts/nodes. May be given as a list or as a string (e.g.,
        '[host1, host2]'
    mapfile_dir : str
        Directory for output mapfile
    filename: str
        Name of output mapfile

    Returns
    -------
    result : dict
        Output datamap filename

    """
    if type(kwargs['output_files']) is str:
        try:
            # Check if input is mapfile containing list as a string
            map_copy = DataMap.load(kwargs['files'])
            in_files = [item.file for item in map_copy]
            files = []
            for f in in_files:
                files += f.strip('[]').split(',')
        except:
            files = kwargs['output_files']
            files = files.strip('[]').split(',')
        files = [f.strip() for f in files]
    if type(kwargs['hosts']) is str:
        hosts = kwargs['hosts'].strip('[]').split(',')
        hosts = [h.strip() for h in hosts]
    mapfile_dir = kwargs['mapfile_dir']
    filename = kwargs['filename']

    for i in range(len(files)-len(hosts)):
        hosts.append(hosts[i])

    if 'input_file' in kwargs:
        file_in = kwargs['input_file']
    else:
        map_in = DataMap.load(kwargs['input_mapfile'])
        file_in = map_in[0].file
    map_out = DataMap([])
    for h, f in zip(hosts, files):
        # Copy file to output, deleting exiting file if needed
        # Note: should we use rsync here instead?
        if os.path.isdir(file_in):
            if os.path.exists(f):
                delete_directory(f)
            shutil.copytree(file_in, f)
        else:
            if os.path.exists(f):
                os.remove(f)
            shutil.copyfile(file_in, f)
        map_out.data.append(DataProduct(h, f, False))

    fileid = os.path.join(mapfile_dir, filename)
    map_out.save(fileid)
    result = {'mapfile': fileid}

    return result
