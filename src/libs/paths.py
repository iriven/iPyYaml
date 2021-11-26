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
import sys
import os
import glob
import re
import errno

currentdir = os.path.dirname(os.path.realpath(__file__))
parentDirectory = os.path.dirname(currentdir)
srcDirectory = os.path.dirname(parentDirectory)
sys.path.append(os.path.abspath(parentDirectory))
sys.path.append(os.path.abspath(srcDirectory))

from libs.common import main, singleton

@singleton
class FileSystem(object):
    def __init__(self):
        self.__INVALID_PATHNAME_ERROR = 123
        self.__DIR_MODE = 0o755
        self.__FILE_MODE = 0o775
        self.DirectorySeparator = os.path.sep

    def isDirectory(self, sPath)->bool:
        try:
            if not(self.isValidPathname(sPath)):
                return False
            return os.path.isdir(os.path.expanduser(sPath))
        except TypeError:
            return False

    def isFile(self, sPath)->bool:
        try:
            if not(self.isValidPathname(sPath)):
                return False
            return os.path.isfile(os.path.expanduser(sPath))
        except TypeError:
            return False

    def exists(self, sPath)->bool:
        try:
            if not(self.isValidPathname(sPath)):
                return False
            return os.path.exists(os.path.expanduser(sPath))
        except TypeError:
            return False

    def isValidPathname(self, pathname: str)->bool:
        try:
            if not isinstance(pathname, str) or not pathname:
                return False
            _, pathname = os.path.splitdrive(os.path.expanduser(pathname))
            root_dirname = os.environ.get('HOMEDRIVE', 'C:') if sys.platform == 'win32' else os.path.sep
            assert os.path.isdir(root_dirname)
            pathHandler = root_dirname.rstrip(os.path.sep) + os.path.sep
            for pathname_part in (pathname.strip(os.path.sep)).split(os.path.sep):
                try:
                    pathHandler += pathname_part + os.path.sep
                    os.lstat(pathHandler)
                except OSError as exc:
                    if hasattr(exc, 'winerror'):
                        if exc.winerror == self.__INVALID_PATHNAME_ERROR:
                            return False
                    elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                        return False
        except TypeError as exc:
            return False
        else:
            return True

    def makeDirectory(self, sPath: str):
        if self.isValidPathname(sPath):
            if not sPath or os.path.exists(os.path.expanduser(sPath)):
                return []
            (head, tail) = os.path.split(os.path.expanduser(sPath))  # head/tail
            res = self.makeDirectory(head)
            os.mkdir(os.path.expanduser(sPath))
            os.chmod(os.path.expanduser(sPath), self.__DIR_MODE)
            res += [sPath]
            return res

    def removeDirectory(path):
        # os.removedirs(name)
        pass

    def clearDirectory(path):
        pass

    def touch(self, sPath)->bool:
        try:
            if self.isValidPathname(sPath):
                if not self.exists(sPath):
                    __TargetDirectory = os.path.dirname(os.path.realpath(os.path.expanduser(sPath)))
                    if not self.exists(__TargetDirectory):
                        self.makeDirectory(__TargetDirectory)
                    with open(os.path.expanduser(sPath), 'w') as stream:
                        pass
                    stream.close()
                    os.chmod(os.path.expanduser(sPath), self.__FILE_MODE)
                return True
            return False
        except TypeError:
            return False

    def isWritable(self, sPath)->bool:
        try:
            if self.isValidPathname(sPath):
                if not self.exists(sPath):
                    __TargetDirectory = os.path.dirname(os.path.realpath(os.path.expanduser(sPath)))
                    if not __TargetDirectory:
                        __TargetDirectory = '.'
                    return os.access(__TargetDirectory, os.W_OK)
                if self.isFile(sPath):
                    return os.access(os.path.expanduser(sPath), os.W_OK)
            return False
        except TypeError:
            return False

    def isReadable(self, sPath)->bool:
        try:
            if self.isValidPathname(sPath):
                if not self.exists(sPath):
                    return False
                if self.isFile(sPath) and os.access(os.path.expanduser(sPath), os.R_OK):
                    with open(os.path.expanduser(sPath)) as fp:
                        return fp.read()
            return False
        except TypeError:
            return False

    def unlink(self, sPath)->bool:
        try:
            if self.isReadable(sPath):
                os.remove(os.path.expanduser(sPath), '*' , dir_fd=None)
                return True
            return False
        except TypeError:
            return False

    def glob(self, location: str, pattern: str, recursive=False)->list:
        try:
            output = []
            if self.isValidPathname(location):
                if self.isFile(location):
                    location = os.path.dirname(os.path.expanduser(location))
                location = location.rstrip(self.DirectorySeparator)
                filePath = os.path.normcase(location)
                if self.exists(filePath):
                    pattern = pattern.strip('*')
                    pattern = os.path.join(filePath, '*' + pattern + '*')
                    output = [f for f in glob.glob(pattern, recursive = recursive) if not re.match(r'.*\__pycache__.*', f)]
            return output
        except IOError  as e:
            return False

if __name__ == '__main__':
    sys.exit(main(__file__))

