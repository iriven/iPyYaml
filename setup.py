# installation: pip install nested-lookup
from setuptools import setup, find_packages

# get list of requirement strings from requirements.txt
def remove_whitespace(x):
    return ''.join(x.split())

def sanitize(x):
    return not x.startswith('#') and x != ''

def requirements():
    with open('requirements.pip', 'r') as f:
        r = f.readlines()
    map(remove_whitespace, r)
    filter(sanitize, r)
    return r

if __name__ == '__main__':
    print(requirements())
    setup(
        name='ifileconverter',
        packages=find_packages(),
        version='0.1.0',
        description='A python Yaml parser and dumper based on PyYAML',
        long_description=open('README.rst').read(),
        keywords = ['yaml', 'parser', 'dumper'],
        author='Alfred TCHONDJO',
        author_email='atchondjo@gmail.com',
        license='MIT',
        platforms=['All'],
        include_package_data=True,
        py_modules=['ipyyaml'],
        install_requires=['pkgutil','pyyaml'],
        python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
        classifiers=[
            # this library supports the following Python versions.
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
        ],
    )
