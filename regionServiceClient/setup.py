#!/usr/bin/env python
"""Setup module for cloud-regionsrv-client"""

try:
    import setuptools
except ImportError:
    sys.stderr.write('Python setuptools required, please install.')
    sys.exit(1)

if __name__ == '__main__':
     pkg = setuptools.find_packages('lib')
     setuptools.setup(
        name='cloudregister',
        description=('Register a cloud guest with an SMT server'),
        url='https://github.com/SUSE/pubcloud',
        license='LGPL-3.0',
        author='SUSE',
        author_email='public-cloud-dev@susecloud.net',
        version='6.0.0',
        packages=setuptools.find_packages('lib'),
        package_dir={
            '': 'lib',
        }
     )
