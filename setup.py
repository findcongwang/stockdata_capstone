import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stockdata_capstone",
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
    package_dir={"": "stockdata_capstone"},
    packages=setuptools.find_packages(where="stockdata_capstone"),
    python_requires=">=3.9",
)