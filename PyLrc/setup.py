import setuptools

with open("../README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MyLyric",
    version="2.0.0",
    author="Ding Zedong",
    author_email="2701690963@qq.com",
    description="A small, light lyric file process package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GNU AGPLv3",
        "Operating System :: OS Independent",
    ],
)