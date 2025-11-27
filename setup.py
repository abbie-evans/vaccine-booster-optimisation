from setuptools import setup, find_packages

def get_readme():
    """
    Load README.md text for use as description.
    """
    with open('README.md') as f:
        return f.read()

setup(
    name='vaccbopti',
    version='0.1',
    description='A package to model vaccine booster optimisation',
    long_description=get_readme(),
    author='AnMei Daniels, Monica Dewi, Kristijonas Raibuzis, Bente Vissel',
    url='https://github.com/abbie-evans/vaccine-booster-optimisation',
    packages=['vaccbopti'],
    install_requires=[
        # Dependencies go here
        'numpy',
        'matplotlib',
        'pandas',
        'scipy',
    ],
    extras_require={
        #Can include when we start having read the docs
    # 'docs': [
    #     # Sphinx for doc generation. Version 1.7.3 has a bug:
    #     'sphinx>=1.5, !=1.7.3',
    #     # Nice theme for docs
    #     'sphinx_rtd_theme',
    # ],
    'dev': [
        # Flake8 for code style checking
        'flake8>=3',
        'pytest',
        'pytest-cov',
    ],}, 
    license='GPLv3')
