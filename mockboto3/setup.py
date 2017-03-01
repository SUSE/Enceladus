#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

with open('README.asciidoc') as readme_file:
    readme = readme_file.read()

requirements = [
    'boto3',
]

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
    'coverage',
    'pytest-cov',
    'pytest',
]

dev_requirements = [
    'bumpversion',
    'flake8',
    'pip>=7.0.0',
    'Sphinx'
] + test_requirements

setup(
    name='mockboto3',
    version='0.1.1',
    description="Python3 package for mocking the boto3 library.",
    long_description=readme,
    author="SUSE",
    author_email='public-cloud-dev@susecloud.net',
    url='https://github.com/SUSE/Enceladus/mockboto3',
    packages=find_packages(),
    package_dir={'mockboto3':
                 'mockboto3'},
    include_package_data=True,
    install_requires=requirements,
    setup_requires=setup_requirements,
    tests_require=test_requirements,
    extras_require={
        'dev': dev_requirements
    },
    license="MIT license",
    zip_safe=False,
    keywords='mockboto3',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
