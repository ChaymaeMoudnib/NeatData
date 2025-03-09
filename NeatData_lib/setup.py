from setuptools import setup, find_packages

setup(
    name='NeatData',  # Name of your library
    version='0.1.0',           # Version number
    author='Your Name',        # Your name
    author_email='chaymaemoudnibe@gmail.com',  # Your email
    description='A library for data cleaning and visualization.',  # Short description
    long_description=open('README.md').read(),  # Long description from README
    long_description_content_type='text/markdown',  # Format of the long description
    url=' https://github.com/ChaymaeMoudnib/NeatData',  # URL to your repository
    packages=find_packages(),  # Automatically find packages in the directory
    install_requires=[         # List of dependencies
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
    ],
    classifiers=[              # Metadata about your library
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',   # Minimum Python version required
)