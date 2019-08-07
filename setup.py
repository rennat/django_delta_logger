import setuptools


with open('README.md', 'r') as file_handle:
    long_description = file_handle.read()


setuptools.setup(
    name='django_delta_logger',
    version='0.1.0',
    author='Tanner Netterville',
    author_email='tannern@gmail.com',
    description='Model instance change logging for django models.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=None,
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    install_requires=(
        'django>=2.2',
    ),
    test_suite='tests.run_test_suite',
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    )
)
