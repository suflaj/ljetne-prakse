from setuptools import find_packages, setup


def readme(path: str = "./README.md"):
    with open(path) as f:
        return f.read()


setup(
    name="ljetne-prakse",
    version="0.1.0.dev1",
    description="FER Ljetne prakse",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/suflaj/ljetne-prakse",
    author="Miljenko Šuflaj",
    author_email="headsouldev@gmail.com",
    license="Apache License 2.0",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Framework :: Flake8",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="fer ljetne stručne prakse",
    project_urls={
        "Source": "https://github.com/suflaj/ljetne-prakse",
        "Issues": "https://github.com/suflaj/ljetne-prakse/issues",
    },
    packages=find_packages(
        include=(
            "ljetne_prakse",
            "ljetne_prakse.*",
        )
    ),
    install_requires=[
        "beautifulsoup4",
        "html2markdown",
        "requests",
        "tqdm",
    ],
    python_requires=">=3.9",
    package_data={
        "demonstration": ["demo/*"],
        "scripts": ["scripts/*"],
    },
    include_package_data=True,
    zip_safe=False,
)
