"""
Copyright 2011 Ryan Fobel and Christian Fobel

This file is part of Microdrop.

Microdrop is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Microdrop is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Microdrop.  If not, see <http://www.gnu.org/licenses/>.
"""

import os

from utility import path

def hardware_path():
    test_dir = path(os.getcwd())
    while test_dir and not (test_dir / path('hardware')).isdir():
        test_dir = test_dir.parent
    if not test_dir:
        raise Exception('''Could not find 'hardware' directory''')
    return test_dir / path('hardware')