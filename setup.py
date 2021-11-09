'''
Author: Zeng Siwei
Date: 2021-07-12 16:15:50
LastEditors: Zeng Siwei
LastEditTime: 2021-11-09 17:06:43
Description: 
'''

#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages

import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='deepdraughts',
    version='1.2.0',
    author='EndlessLethe',
    author_email='zengsw_study@qq.com',
    url='https://github.com/EndlessLethe/DeepDraughts',
    description=u'A library for playing draughts with AI',
    keywords="draughts MCTS checker deep neural network",
    python_requires='>=3.6',
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
                    'numpy<1.20.0,>=1.17.0', # numpy for py36
                    'pygame>=2.1.0',
                    'requests>=2.24.0',
                    'torch<=1.10.0,>=1.6.0',
                    'tensorboardX>=2.4',
                    ],
    license="GPLv2",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
    ],
    data_files=[('resources', ['resources/endgame1p.pkl', 
                                'resources/endgame2p.pkl', 
                                'resources/endgame3p.pkl', 
                                'resources/endgame4p.pkl'])
                ],
    include_package_data=True,

)