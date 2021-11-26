#coding: utf-8
# Header_start
##############################################################################################
#                                                                                            #
#  Author:         Alfred TCHONDJO - (Iriven France)                                         #
#  Date:           2021-08-18                                                                #
#  Website:        https://github.com/iriven?tab=repositories                                #
#                                                                                            #
# ------------------------------------------------------------------------------------------ #
#                                                                                            #
#  Project:        iRepoBuilder                                                              #
#  Description:    A Python YAML manager Tool                              .                 #
#  Version:        1.0.0    (G1R0C0)                                                         #
#                                                                                            #
#  License:      GNU GPLv3                                                                   #
#                                                                                            #
#  This program is free software: you can redistribute it and/or modify                      #
#  it under the terms of the GNU General Public License as published by                      #
#  the Free Software Foundation, either version 3 of the License, or                         #
#  (at your option) any later version.                                                       #
#                                                                                            #
#  This program is distributed in the hope that it will be useful,                           #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of                            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                             #
#  GNU General Public License for more details.                                              #
#                                                                                            #
#  You should have received a copy of the GNU General Public License                         #
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.                     #
#                                                                                            #
# ------------------------------------------------------------------------------------------ #
#  Revisions                                                                                 #
#                                                                                            #
#  - G1R0C0 :        Creation du module le 18/08/2021 (AT)                                   #
#                                                                                            #
##############################################################################################
# Header_end

import os
import sys

def main(filePath:str = __file__)->str:
    return 'Direct access not allowed to: ' + os.path.basename(filePath)

def lowercaseKeys(obj):
    if isinstance(obj, dict):
        obj = {key.lower(): value for key, value in obj.items()}
    for key, value in obj.items():
        if isinstance(value, list):
            for idx, item in enumerate(value):
                value[idx] = lowercaseKeys(item)
        obj[key] = lowercaseKeys(value)
    return obj

singleton = lambda c: c()

if __name__ == '__main__':
    sys.exit(main())
