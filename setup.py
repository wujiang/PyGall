import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy>=0.6,<=0.6.99',
    'SQLAHelper',
    'pyramid_tm',
    'WebError',
    "gp.fileupload>=1.0,<=1.0.99",
    "PIL>=1.1.4,<=1.1.99",
    ]

setup(name='PyGall',
      version='0.8dev',
      description='Image gallery built with Pyramid web framework',
      long_description=README + '\n\n' +  CHANGES,
      author='Bruno Binet',
      author_email='binet.bruno@gmail.com',
      url='http://gitorious.org/PyGall',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
        'Framework :: Pylons',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Multimedia :: Graphics :: Viewers',
        ],
      keywords='web wsgi pylons pyramid image photo web gallery',
      license='BSD',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="pygall",
      entry_points = """\
      [paste.app_factory]
      main = pygall:main
      """,
      paster_plugins=['PasteScript', 'pyramid'],
      )

