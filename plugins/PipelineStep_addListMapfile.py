import os
from lofarpipe.support.data_map import DataMap, DataProduct
import casacore.tables as ct
try:
  basestring
except NameError:
  basestring = str

def plugin_main(args, **kwargs):
    """
    Makes a mapfile for list of files

    Parameters
    ----------
    files : list or str
        List of files or mapfile with such a list as the only entry. May be
        given as a list of strings or as a string (e.g.,
        '[s1.skymodel, s2.skymodel]'
    hosts : list or str
        List of hosts/nodes. May be given as a list or as a string (e.g.,
        '[host1, host2]'
    check_files_exist : bool
        If True, check that the files exists. If a file does not exist, set skip = True in
        the output mapfile. Default is False
    check_ms_column : str
        Name of the column to check for if the input files are measurement sets. If the
        column is not found, set skip = True in the output mapfile
    mapfile_dir : str
        Directory for output mapfile
    filename: str
        Name of output mapfile

    Returns
    -------
    result : dict
        Output datamap filename

    """
    if type(kwargs['files']) is str:
        try:
            # Check if input is mapfile containing list as a string
            map_in = DataMap.load(kwargs['files'])
            in_files = [item.file for item in map_in]
            files = []
            for f in in_files:
                files += f.strip('[]').split(',')
        except IOError:
            files = kwargs['files']
            files = files.strip('[]').split(',')
        files = [f.strip() for f in files]
    if type(kwargs['hosts']) is str:
        hosts = kwargs['hosts'].strip('[]').split(',')
        hosts = [h.strip() for h in hosts]
    mapfile_dir = kwargs['mapfile_dir']
    filename = kwargs['filename']
    if 'check_files_exist' in kwargs:
        check_files_exist = string2bool(kwargs['check_files_exist'])
    else:
        check_files_exist = False
    if 'check_ms_column' in kwargs:
        check_ms_column = kwargs['check_ms_column']
    else:
        check_ms_column = None


    for i in range(len(files)-len(hosts)):
        hosts.append(hosts[i])

    map_out = DataMap([])
    for h, f in zip(hosts, files):
        skip = False
        if check_files_exist:
            skip = not os.path.exists(f)
            if not skip and check_ms_column is not None:
                try:
                    t = ct.table(f, ack=False)
                    if check_ms_column not in t.colnames():
                        skip = True
                    t.close()
                except RuntimeError:
                    skip = True
        map_out.data.append(DataProduct(h, f, skip))

    fileid = os.path.join(mapfile_dir, filename)
    map_out.save(fileid)
    result = {'mapfile': fileid}

    return result


def string2bool(instring):
    if not isinstance(instring, basestring):
        raise ValueError('string2bool: Input is not a basic string!')
    if instring.upper() == 'TRUE' or instring == '1':
        return True
    elif instring.upper() == 'FALSE' or instring == '0':
        return False
    else:
        raise ValueError('string2bool: Cannot convert string "'+instring+'" to boolean!')
