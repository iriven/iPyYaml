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
import io
import yaml
from collections import OrderedDict

currentdir = os.path.dirname(os.path.realpath(__file__))
parentDirectory = os.path.dirname(currentdir)
sys.path.append(os.path.abspath(parentDirectory))

from libs.common import main
from libs.paths import FileSystem

class iYamlSafeLoader(yaml.SafeLoader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """
    def buildUnicode(self, node):
        '''
        All strings should be Unicode objects, regardless of contents.
        '''
        return self.construct_scalar(node)

    def buildYamlMap(self, node):
        '''
        Use ordered dictionaries for every YAML map.
        '''
        data = OrderedDict()
        yield data
        value = self.__createMapping(node)
        data.update(value)

    def __createMapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(
                None, None,
                u'expected a mapping node, but found %s' % node.id,
                node.start_mark
            )

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as exc:
                raise yaml.constructor.ConstructorError(
                    u'while constructing a mapping',
                    node.start_mark, 'found unacceptable key (%s)' % exc,
                    key_node.start_mark
                )
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

    # Allow bare strings to begin with %. Directives are still detected.
    def check_plain(self):
        plain = super(iYamlSafeLoader, self).check_plain()
        return plain or self.peek() == '%'

    @staticmethod
    def add_constructors(loader):
        loader.add_constructor('tag:yaml.org,2002:str', iYamlSafeLoader.buildUnicode)
        loader.add_constructor('tag:yaml.org,2002:map', iYamlSafeLoader.buildYamlMap)
        loader.add_constructor('tag:yaml.org,2002:omap', iYamlSafeLoader.buildYamlMap)

#register the constructor
iYamlSafeLoader.add_constructors(iYamlSafeLoader)

class iYamlSafeDumper(yaml.SafeDumper):
    '''
    Custom yaml representer class
    @see: yaml.representer.represent_mapping
    '''
    def increase_indent(self, flow=False, indentless=False):
        return super(iYamlSafeDumper, self).increase_indent(flow, False)

    def represent_list(self, data):
        """If a list has less than 4 items, represent it in inline style
        (i.e. comma separated, within square brackets).
        """
        node = super(iYamlSafeDumper, self).represent_list(data)
        length = len(data)
        if self.default_flow_style is None and length < 5:
            node.flow_style = True
        elif self.default_flow_style is None:
            node.flow_style = False
        return node
    #represent boolean
    def represent_bool(self, data):
        if data:
            value = u'true'
        else:
            value = u'false'
        return self.represent_scalar('tag:yaml.org,2002:bool', value)
    #represent none type
    def represent_none(self, data):
        """Represent a None value with nothing instead of 'none'.
        """
        return self.represent_scalar('tag:yaml.org,2002:null', '')
    #represent string
    def represent_str(self, data: str):
        if os.linesep in data:
            return self.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return self.represent_scalar('tag:yaml.org,2002:str', data)
    #represent mapping
    def represent_orderedDict(self, data):
        return self.represent_mapping('tag:yaml.org,2002:map', data.items())

    @staticmethod
    def add_representers(dumper):
        dumper.add_representer(OrderedDict, iYamlSafeDumper.represent_orderedDict)
        dumper.add_representer(dict, iYamlSafeDumper.represent_orderedDict)
        dumper.add_representer(bool, iYamlSafeDumper.represent_bool)
        dumper.add_representer(type(None), iYamlSafeDumper.represent_none)
        dumper.add_representer(str, iYamlSafeDumper.represent_str)
        dumper.add_representer(list, iYamlSafeDumper.represent_list)

#register the representer
iYamlSafeDumper.add_representers(iYamlSafeDumper)

class iYamlLoader(object):
    '''
    Custom yaml loader class
    '''
    def __init__(self, **kwargs) -> any:
        if kwargs is None:
            kwargs = {}
        kwargs.setdefault('Loader', iYamlSafeLoader)
        kwargs.setdefault('Dumper', iYamlSafeDumper)
        kwargs.setdefault('flowstyle', False)
        kwargs.setdefault('allow_unicode', True)
        kwargs.setdefault('indent', 4)
        self.__loader = kwargs.get('Loader')
        self.Dumper = kwargs.get('Dumper')
        self.Dumper.ignore_aliases = lambda self, data: True
        yaml.add_constructor(self.__loader, iYamlSafeLoader.add_constructors)
        yaml.add_representer(self.Dumper, iYamlSafeDumper.add_representers)
        self.flowstyle =  kwargs.get('flowstyle')
        self.encoding = kwargs.get('encoding', 'utf-8')
        self.acceptUnicode =  kwargs.get('allow_unicode')
        self.__sourceFile = None
        self._FileContent = OrderedDict()
        self._extractedNode = OrderedDict()
        if kwargs.get('filePath', None):
            self.setDestinationPath(self, kwargs.get('filePath'))
        self.data = OrderedDict()

    def load(self, oSource)->any:
        '''
        load data from a given file or dictionary
        '''
        try:
            yamlDatas = None
            if not(FileSystem.isValidPathname(oSource)):
                if not oSource:
                    yamlDatas = OrderedDict()
                elif type(oSource) in (str, dict, OrderedDict, list, tuple):
                    try:
                        yamlDatas = yaml.load(yaml.dump(oSource,
                                default_flow_style=self.flowstyle,
                                allow_unicode=self.acceptUnicode,
                                encoding=self.encoding,
                                Dumper=self.Dumper),
                            Loader=self.__loader)
                    except yaml.YAMLError as exc:
                        print(exc)
            else:
                if not(FileSystem.exists(oSource)):
                    raise ValueError('Yaml Loader error: Input file [' + str(oSource) + '] does not exists')
                self.__sourceFile = oSource
                with io.open(self.__sourceFile, 'r', encoding=self.encoding) as stream:
                    try:
                        yamlDatas = yaml.load(stream,Loader=self.__loader)
                    except yaml.YAMLError as exc:
                        print(exc)
        except ValueError as e:
            sys.exit(e)
        if yamlDatas is not None and len(yamlDatas) > 0:
            self._FileContent = yamlDatas
        return self._FileContent

class iYamlDumper(iYamlLoader):
    """
    Keep yaml human readable/editable.  Disable yaml references.
    """
    def __init__(self, **kwargs) -> None:
        if kwargs is None:
            kwargs = {}
        kwargs.setdefault('Loader', iYamlSafeLoader)
        kwargs.setdefault('Dumper', iYamlSafeDumper)
        kwargs.setdefault('flowstyle', False)
        kwargs.setdefault('allow_unicode', True)
        kwargs.setdefault('sort_keys', False)
        kwargs.setdefault('indent', 2)
        kwargs.setdefault('eol', os.linesep)
        kwargs.setdefault('explicit_start', True)
        kwargs.setdefault('width', 4096)
        super().__init__(**kwargs)
        self.sortKeys =  kwargs.get('sort_keys')
        self.acceptUnicode =  kwargs.get('allow_unicode')
        self.Dumper = kwargs.get('Dumper')
        self.Dumper.ignore_aliases = lambda self, data: True
        yaml.add_representer(self.Dumper, iYamlSafeDumper.add_representers)
        yaml.preserve_quotes = True
        self.flowstyle =  kwargs.get('flowstyle')
        self.overwrite = kwargs.get('overwrite', True)
        self.encoding = kwargs.get('encoding', 'utf-8')
        self.indent = kwargs.get('indent')
        self.explicitStart = kwargs.get('explicit_start')
        self.width = kwargs.get('width')
        self.tab = '\t'
        self.fileExtension = '.yml'
        self.__destDirectory = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs')
        self.__destFile = None
        self.filePath = None
        if kwargs.get('filePath', None):
            self.setDestinationPath(self, kwargs.get('filePath'))
        self.data = {}

    def setDestinationPath(self, yamlFile: str)-> bool:
        '''
        Set the gerenerated file destination path
        '''
        try:
            filePath = yamlFile if yamlFile.endswith(self.fileExtension ) else yamlFile + self.fileExtension
            if not FileSystem.isValidPathname(filePath):
                raise ValueError('Invalid file path: [' + str(yamlFile) + ']')
            if FileSystem.exists(filePath) and not self.overwrite:
                raise Exception("Yaml file '%s' exists as '%s" % (yamlFile, filePath))
            if not(os.path.basename(yamlFile) == yamlFile):
                self.__destDirectory = os.path.dirname(os.path.realpath(yamlFile))
            self.filePath = os.path.join(self.__destDirectory, os.path.splitext(os.path.basename(yamlFile))[0] + self.fileExtension)
            if not os.path.exists(self.__destDirectory) or not os.path.isdir(self.__destDirectory):
                FileSystem.makeDirectory(self.__destDirectory)
            return True
        except Exception as e:
            raise e

    def save(self, filePath: str = None):
        '''
        gerenerate the desired file
        '''
        try:
            if filePath:
                self.setDestinationPath(filePath)
            if not isinstance(self._FileContent, dict):
                if type(self._FileContent).__name__ not in ('list', 'tuple'):
                    self._FileContent = dict([self._FileContent])
            with open(self.filePath, 'w', encoding=self.encoding) as streaming:
                yaml.dump(self._FileContent,
                        stream=streaming,
                        default_flow_style=self.flowstyle,
                        allow_unicode=self.acceptUnicode,
                        indent=self.indent,
                        encoding=self.encoding,
                        explicit_start=self.explicitStart,
                        width=self.width,
                        Dumper=self.Dumper)
                streaming.close()
        except IOError  as e:
            sys.exit('I/O error(%s): %s' % (e.errno, e.strerror))

if __name__ == '__main__':
    sys.exit(main(__file__))

