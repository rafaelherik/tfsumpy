from setuptools import setup, find_packages

setup(
    name='tfsumpy',
    version='0.0.1-alpha',
    description='A Python tool for Terraform state summary and analysis',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Notry',
    author_email='support@notry.cloud',
    url='https://github.com/notry-cloud/tfsumpy',
    packages=find_packages(),
    package_data={
        'tfsumpy': ['rules_config.json'],
    },
    entry_points={
        'console_scripts': [
            'tfsumpy=tfsumpy.__main__:main'
        ]
    },
    python_requires='>=3.10',
    install_requires=[
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Build Tools',
        'Topic :: System :: Systems Administration',
    ],
    keywords='terraform, infrastructure, cloud, DevOps',
)   