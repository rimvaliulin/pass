import os
import codecs
from distutils.core import setup

version = __import__('Pass').get_version()

long_description = codecs.open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='Pass',
    version=version,
    author='Rim Valiulin',
    author_email='rim.valiulin@gmail.com',
    url='https://github.com/rimvaliulin/pass',
    download_url='https://github.com/rimvaliulin/pass',
    license='BSD',
    description='The pythonic awesome stylesheet language',
    long_description=long_description,
    keywords=('css,css3,process pass,css nesting,css variable,css,gradients css,gradients css3,pass compiler,pass css,'
        'pass inheritance,pass,nested css,parser,preprocessor,bootstrap css,bootstrap pass,'
        'style,styles,stylesheet,variables in css,css pass'),
    packages=['Pass'],
    scripts=['django/bin/pass'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
    ],
)

