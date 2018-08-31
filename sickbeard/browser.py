# Author: Nic Wolfe <nic@wolfeden.ca>
# URL: http://code.google.com/p/sickbeard/
#
# This file is part of SickGear.
#
# SickGear is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SickGear is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SickGear.  If not, see <http://www.gnu.org/licenses/>.

import os
import string

from sickbeard import encodingKludge as ek
from sickbeard import logger


# use the built-in if it's available (python 2.6), if not use the included library
try:
    import json
except ImportError:
    from lib import simplejson as json

# this is for the drive letter code, it only works on windows
if 'nt' == os.name:
    from ctypes import windll


# adapted from
# http://stackoverflow.com/questions/827371/is-there-a-way-to-list-all-the-available-drive-letters-in-python/827490
def getWinDrives():
    """ Return list of detected drives """
    assert 'nt' == os.name

    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1

    return drives


def foldersAtPath(path, includeParent=False, includeFiles=False):
    """ Returns a list of dictionaries with the folders contained at the given path
        Give the empty string as the path to list the contents of the root path
        under Unix this means "/", on Windows this will be a list of drive letters)
    """

    logger.log(u'Path %s' % path)
    
    # walk up the tree until we find a valid path
    while path and not ek.ek(os.path.isdir, path):
        if path == ek.ek(os.path.dirname, path):
            path = ''
            break
        else:
            path = ek.ek(os.path.dirname, path)

    if '' == path:
        if 'nt' == os.name:
            entries = [{'currentPath': '\My Computer'}]
            for letter in getWinDrives():
                letter_path = '%s:\\' % letter
                entries.append({'name': letter_path, 'path': letter_path})
            return entries
        elif os.path.exists('/system/bin/getprop'):
            logger.log(u'Android')
            path = '$HOME/storage/'
            logger.log(u'Path %s' % path)
        else:
            path = '/'

    # fix up the path and find the parent
    path = ek.ek(os.path.abspath, ek.ek(os.path.normpath, path))
    parent_path = ek.ek(os.path.dirname, path)

    # if we're at the root then the next step is the meta-node showing our drive letters
    if 'nt' == os.name and path == parent_path:
        parent_path = ''

    try:
        file_list = get_file_list(path, includeFiles)
    except OSError as e:
        logger.log(u'Unable to open %s: %r / %s' % (path, e, e), logger.WARNING)
        file_list = get_file_list(parent_path, includeFiles)

    file_list = sorted(file_list, lambda x, y: cmp(ek.ek(os.path.basename, x['name']).lower(),
                                                   ek.ek(os.path.basename, y['path']).lower()))

    entries = [{'currentPath': path}]
    if includeParent and path != parent_path:
        entries.append({'name': '..', 'path': parent_path})
    entries.extend(file_list)

    return entries


def get_file_list(path, include_files):

    result = []

    hide_names = [
        # windows specific
        'boot', 'bootmgr', 'cache', 'config.msi', 'msocache', 'recovery', '$recycle.bin', 'recycler',
        'system volume information', 'temporary internet files',
        # osx specific
        '.fseventd', '.spotlight', '.trashes', '.vol', 'cachedmessages', 'caches', 'trash',
        # general
        '.git']

    # filter directories to protect
    for name in ek.ek(os.listdir, path):
        if name.lower() not in hide_names:
            path_file = ek.ek(os.path.join, path, name)
            is_dir = ek.ek(os.path.isdir, path_file)
            if include_files or is_dir:
                result.append({'name': name, 'path': path_file, 'isFile': (1, 0)[is_dir]})

    return result
