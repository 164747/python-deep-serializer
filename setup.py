from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='deep_serializer',
    version='0.0.6',
    packages=find_packages(),
    url='https://github.com/164747/python-deep-serializer',
    license=' MIT License',
    author='David Jacquet',
    author_email='jacquet.david@gmail.com',
    platforms=['any'],
    python_requires='>=3.6.0',
    install_requires=[
        'python-dateutil',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    description='Package for deep serializing and deserializing',
    long_description=long_description,
    long_description_content_type="text/markdown"
)
