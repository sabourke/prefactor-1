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
    use_symlinks : bool
        If True, use sym links instead of copying. The input_file will be copied to the
        output directory and the output mapfile will be populated with the copy's path
        in every entry
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
    if 'use_symlinks' in kwargs:
        use_symlinks = string2bool(kwargs['use_symlinks'])
    else:
        use_symlinks = False

    for i in range(len(files)-len(hosts)):
        hosts.append(hosts[i])

    if 'input_file' in kwargs:
        file_in = kwargs['input_file']
    else:
        map_in = DataMap.load(kwargs['input_mapfile'])
        file_in = map_in[0].file

    # If symlinks are used, copy file_in so that it is present in the output path. Then,
    # use this copy in the output mapfile
    if use_symlinks:
        file_in_copy = os.path.join(os.path.dirname(files[0]), os.path.basename(file_in).upper())
        if os.path.isdir(file_in):
            if os.path.exists(file_in_copy):
                delete_directory(file_in_copy)
            shutil.copytree(file_in, file_in_copy)
        else:
            if os.path.exists(file_in_copy):
                os.remove(file_in_copy)
            shutil.copyfile(file_in, file_in_copy)
        file_in = file_in_copy

    map_out = DataMap([])
    for h, f in zip(hosts, files):
        # Copy file to output, deleting exiting file if needed
        if os.path.isdir(file_in):
            if os.path.exists(f):
                delete_directory(f)
            if use_symlinks:
                os.symlink(file_in, f)
            else:
                shutil.copytree(file_in, f)
        else:
            if os.path.exists(f) or os.path.islink(f):
                os.remove(f)
            if use_symlinks:
                os.symlink(file_in, f)
            else:
                shutil.copyfile(file_in, f)
        if use_symlinks:
            map_out.data.append(DataProduct(h, file_in, False))
        else:
            map_out.data.append(DataProduct(h, f, False))

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
