import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wouw",
    version="0.1.0",
    author="Louis Simons",
    author_email="lousimons@gmail.com",
    description="Docx-centric Requirements management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['wouw'],
    install_requires=['python-docx', 'watchdog', 'rich'],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': ['wouw=wouw:main']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
