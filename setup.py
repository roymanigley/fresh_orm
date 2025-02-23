from setuptools import setup

long_description = open('README.md', "rt").read()

setup(
    name='fresh_orm',
    version='0.0.2',
    description='A lightweight SQLite Object-Relational Mapping (ORM) library for Python, designed to simplify database interactions and provide an intuitive interface for managing SQLite tables and relationships.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/roymanigley/fresh_orm',
    author='Roy Manigley',
    author_email='roy.manigley@gmail.com',
    license='MIT',
    packages=['fresh_orm'],
    install_requires=[],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.11',
    ],
)
