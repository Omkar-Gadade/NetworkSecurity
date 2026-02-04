'''
The setup.py file is an essential part of packaging and distributing Python projects. 
It contains metadata about the project and instructions on how to install it. 
This file is used by tools like setuptools to build and install the package.
'''
from setuptools import setup, find_packages
from typing import List

def get_requirements() -> List[str]:
    """Read the requirements from a file and return them as a list."""
    requirement_lst: List[str] = []
    try:
        with open('requirements.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                requirement = line.strip()
                if requirement and requirement!='-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("requirements.txt file not found.")

    return requirement_lst

setup(
    name='networksecurity',
    version='0.0.1',
    author='Omkar Gadade',
    packages=find_packages(),
    install_requires=get_requirements(),
)