import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MyLyric",
    version="2.1.0",
    author="Ding Zedong",
    author_email="2701690963@qq.com",
    license="License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
    description="A small, light lyric file process package",
    keywords=["lyric", "lyric processing", "lyric file", "lrc", "lrc file", "lrc processing", "lrc file process", "PyLrc",
                "MyLyric", "MyLrc"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=["MyLyric"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    include_package_data=True
)