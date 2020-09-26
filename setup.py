import setuptools
from collections import Iterable

def read_file(file_name):
    file_names = (file_name,) if isinstance(file_name, Iterable) else file_name
    contents = []
    for fname in file_names:
        with open(fname, encoding="utf-8") as f:
            contents.append(f.read())
    return "\n".join(contents)

long_description = read_file("README.md")

meta = {}
exec(read_file('./src/pyaz/version.py'), meta)

setuptools.setup(
    name="pyaz",
    version=meta['__version__'],
    author="Ivan Georgiev",
    #author_email="ivan.georgiev",
    description="Pythonic Azure tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ivangeorgiev/pyaz",
    packages=['pyaz'],
    package_dir={'':'src'},
    install_requires=[
        'click',
        'python-dotenv'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points='''
        [console_scripts]
        pyaz=pyaz.cli:cli
    ''',
    python_requires='>=3.6',
)