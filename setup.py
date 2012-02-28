#!/usr/bin/python
# coding: utf-8

"""
Copyright © 2012 Francesco Gigli <jaramir@gmail.com>

pyBGG is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pyBGG is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyBGG.  If not, see <http://www.gnu.org/licenses/>.

"""

import setuptools

setuptools.setup(
    name         = "pyBGG",
    version      = "0.1.1",
    description  = "BoardGameGeek XML API for Python",
    author       = "Francesco Gigli",
    author_email = "jaramir@gmail.com",
    packages     = [ "pyBGG", ],
    test_suite   = "test",
)
