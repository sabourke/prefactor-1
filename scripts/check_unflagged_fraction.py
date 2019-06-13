#!/usr/bin/env python
"""
Flag MS if unflagged fraction is too low.
"""
import argparse
import os
import numpy as np
from lofarpipe.support.data_map import DataMap
from lofarpipe.support.data_map import DataProduct


def find_unflagged_fraction(ms_file):
    """
    Finds the fraction of data that is unflagged
    Parameters
    ----------
    ms_file : str
        Filename of input MS
    Returns
    -------
    unflagged_fraction : float
        Fraction of unflagged data
    """
    import subprocess

    # Call taql. Note that we do not use pt.taql(), as pt.taql() can cause
    # hanging/locking issues on some systems
    p = subprocess.Popen("taql 'CALC sum([select nfalse(FLAG) from {0}]) / "
        "sum([select nelements(FLAG) from {0}])'".format(ms_file),
        shell=True, stdout=subprocess.PIPE)
    r = p.communicate()
    unflagged_fraction = float(r[0])

    return unflagged_fraction


def main(ms_list, filename='check_unflagged.mapfile', mapfile_dir='', min_fraction=0.01, print_fraction=False):
    """
    Flag MS if unflagged fraction is too low.

    Parameters
    ----------
    ms_list : str
        List of names (path) of input MS
    filename: str
        Name of output mapfile
    mapfile_dir : str
        Directory for output mapfile
    min_fraction : float , optional
        minimum fraction of unflagged data needed to keep this MS
    print_fraction : bool, optional
        print the actual fration of unflagged data

    Returns
    -------
    result : dict
        Dict with the name of the input MS or "None"

    """
    ms_list = ms_list.strip('[]').split(',')
    ms_list = [f.strip() for f in ms_list]
    min_fraction = float(min_fraction)
    flag_map_out = DataMap([])
    fraction_map_out = DataMap([])
    for ms_file in ms_list:
        unflagged_fraction = find_unflagged_fraction(ms_file)
        if print_fraction:
            print("File %s has %.2f%% unflagged data."%(os.path.basename(ms_file),unflagged_fraction*100.))
        if unflagged_fraction < min_fraction:
            print('check_unflagged_fraction.py: Unflagged fraction of {0} is: {1}, '
                  'removing file.'.format(os.path.basename(ms_file), str(unflagged_fraction)))
            flag_map_out.append(DataProduct('localhost', 'None', False))
        else:
            flag_map_out.append(DataProduct('localhost', ms_file, False))
        fraction_map_out.append(DataProduct('localhost', unflagged_fraction, False))

    flagmapname = os.path.join(mapfile_dir, filename)
    flag_map_out.save(flagmapname)
    fractionmapname = os.path.join(mapfile_dir, 'unflagged_fraction.mapfile')
    fraction_map_out.save(fractionmapname)


if __name__ == '__main__':
    descriptiontext = "Check a MS for a minimum fraction of unflagged data.\n"

    parser = argparse.ArgumentParser(description=descriptiontext, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('inputms', help='name of the input MS')
    parser.add_argument('-f', '--min_fraction', help='Minimum fraction of unflagged data needed to keep this MS '
                        '(default 0.01 = "keep if at least 1%% is not flagged")',  type=float, default=0.01)
    args = parser.parse_args()

    erg = main(args.inputms, args.min_fraction,print_fraction=True)
