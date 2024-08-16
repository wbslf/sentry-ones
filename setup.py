#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="sentry-ones",
    version='0.3.2',
    author='mudongshier',
    author_email='lf1240560813@gmail.com',
    url='https://github.com/wbslf/sentry-ones',
    description='A Sentry extension which send errors stats to Ones',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords='sentry ones',
    include_package_data=True,
    zip_safe=False,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        'sentry>=9.0.0',
        'requests>=2.20.1',
    ],
    entry_points={
        'sentry.plugins': [
            'sentry_ones = sentry_ones.plugin:OnesPlugin'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 2.7',
        "License :: OSI Approved :: MIT License",
    ]
)
