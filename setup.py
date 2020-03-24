import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="isabellyrocha",
    version="0.0.1",
    author="Isabelly Rocha",
    author_email="isabelly.rocha@unine.ch",
    description="PipeTune is a library for hyper and system parameters tuning.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/isabellyrocha/pipetune",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
