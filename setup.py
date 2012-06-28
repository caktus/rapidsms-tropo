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
    url='http://github.com/caktus/rapidsms-tropo/',
    license='LICENSE.txt',
    description='RapidSMS Tropo Threadless Backend',
    long_description=open('README.rst').read(),
    install_requires=(
        'rapidsms-threadless-router>=0.1.1',
        'tropo-webapi-python>=0.1.1',
    ),
)
