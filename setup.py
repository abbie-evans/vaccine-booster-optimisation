from setuptools import setup, find_packages


def get_readme():
    """Load README.md text for use as description."""
    with open('README.md') as f:
        return f.read()


setup(name='vaccbopti',
      version='0.1',
      description='A package to model vaccine booster optimisation',
      long_description=get_readme(),
      author='AnMei Daniels, Monica Dewi, Kristijonas Raibuzis, Bente Vissel',
      url='https://github.com/abbie-evans/vaccine-booster-optimisation',
      # Packages to include
      packages=find_packages(include=('vaccbopti', 'vaccbopti.*')),
      install_requires=['numpy',
                        'pandas',
                        'matplotlib',
                        'scipy',
                        'shiny'],
      extras_require={'docs': ['sphinx>=1.5, !=1.7.3',  # Sphinx for doc generation (v.1.7.3 has a bug)
                               'sphinx_rtd_theme'],  # Nice theme for docs
                      'dev': ['flake8>=3',  # Flake8 for code style checking
                              'pytest',
                              'pytest-cov']},
      license='GPLv3')
