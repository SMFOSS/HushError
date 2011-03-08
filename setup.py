from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='HushError',
      version=version,
      description="",
      long_description=""" """,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='whit at surveymonkey.com',
      author_email='whit at surveymonkey.com',
      url='http://github.com/SurveyMonkey/HushError',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=["webob"],
      entry_points="""
      """,
      )
