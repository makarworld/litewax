from setuptools import setup, find_packages

"""
:author: abuztrade
:license: MIT License, see LICENSE file.
:copyright: (c) 2022 by abuztrade.
"""


version = '0.0.7'

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="litewax",
    version=version,

    author="abuztrade",
    author_email="abuztrade.work@gmail.com",

    url="https://github.com/makarworld/litewax.git",
    download_url=f"https://github.com/makarworld/litewax/archive/refs/tags/v{version}.zip",

    description="Simply python library for interact with (EOSIO) WAX blockchain",

    packages=['litewax'],
    install_requires=['requests', 'libeospy', 'cloudscraper'],

    license='MIT License',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Communications :: Email",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",

        "Intended Audience :: Developers",
        "Intended Audience :: Customer Service",
        "Intended Audience :: Financial and Insurance Industry",
    ],
    include_package_data=True, # for MANIFEST.in
    python_requires='>=3.6.0',

    package_data={package: ["py.typed", "*.pyi", "**/*.pyi"] for package in find_packages()},
    zip_safe=False,
)