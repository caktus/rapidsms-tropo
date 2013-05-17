from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name='rapidsms-tropo',
    version=__import__('rtropo').__version__,
    author='Caktus Consulting Group',
    author_email='solutions@caktusgroup.com',
    packages=find_packages(),
    include_package_data=True,
    exclude_package_data={
        '': ['*.sql', '*.pyc'],
    },
    url='https://github.com/caktus/rapidsms-tropo/',
    license='LICENSE.txt',
    description='RapidSMS Tropo Threadless Backend',
    long_description=open('README.rst').read(),
    install_requires=(
        'rapidsms>=0.10.0',
        'requests>=1.2.0',
        'django>=1.4',
    ),
    test_suite="runtests.runtests",
    tests_require=(
        'mock',
    )
)
