from setuptools import setup


setup(
    name='postdoc',
    # hey, remember to update postdoc.__version__ too
    version='0.1.4',
    description='A helper for Postgres + Docker that works for free',
    long_description=open('README.rst').read(),
    author='Chris Chang',
    author_email='c@crccheck.com',
    url='https://github.com/crccheck/postdoc',
    py_modules=['postdoc'],
    entry_points={
        'console_scripts': [
            'phd = postdoc:main',
        ],
    },
    license='Apache',
    tests_require=[
        'mock==1.0.1',
    ],
    test_suite='test_postdoc',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Topic :: Utilities',
    ],
)
