from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="stockdata",
    version="0.0.1",
    author="Francis C. Wang",
    author_email="findcongwang@gmail.com",
    description="Working package for data-eng capstone project.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/findcongwang/stockdata_capstone",
    project_urls={
        "Bug Tracker": "https://github.com/findcongwang/stockdata_capstone/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
)