from distutils.core import setup

setup(
    name=b'Pass',
    version=__import__('Pass').get_version(),
    author='Rim Valiulin',
    author_email='rim.valiulin@gmail.com',
    url='https://github.com/rimvaliulin/pass',
    download_url='https://github.com/rimvaliulin/pass',
    license=open('LICENSE').read(),
    description='The pythonic awesome stylesheet language',
    long_description=open('README.rst').read(),
    keywords=('css,css3,process pass,css nesting,css variable,css,gradients css,gradients css3,pass compiler,pass css,'
        'pass inheritance,pass,nested css,parser,preprocessor,bootstrap css,bootstrap pass,'
        'style,styles,stylesheet,variables in css,css pass'),
    packages=['Pass'],
    scripts=['bin/pass'],
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