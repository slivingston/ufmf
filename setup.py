from setuptools import setup, find_packages

kws=dict(
    )

setup(name='motmot.ufmf',
      description='micro-fmf (.ufmf) format library',
      version='0.1',
      author='Andrew Straw',
      author_email='strawman@astraw.com',
      namespace_packages = ['motmot'],
      packages = find_packages(),
      )
