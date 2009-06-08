from setuptools import setup, find_packages

kws=dict(
    )

setup(name='motmot.ufmf',
      description='micro-fmf (.ufmf) format library',
      version='0.2',
      author='Andrew Straw',
      author_email='strawman@astraw.com',
      namespace_packages = ['motmot'],
      packages = find_packages(),
      entry_points = {
    'console_scripts': ['ufmf2fmf = motmot.ufmf.ufmf2fmf:main',
                        'ufmfcat = motmot.ufmf.ufmfcat:main',
                        'playufmf = motmot.ufmf.playufmf:main',
                        'ufmf_from_fmf = motmot.ufmf.ufmf_from_fmf:main',
                        ],
    'motmot.fview.plugins':
    'fview_ufmf_saver = motmot.ufmf.fview_plugin:UFMFFviewSaver',
    }
      )
