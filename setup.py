from setuptools import setup, find_packages

setup(
    name="AmenablePDDL",
    version="0.1.4",
    author="Julius Arolovitch",
    author_email="jarolovi@andrew.cmu.edu",
    description="A high-level PDDL parsing and planning interface for implementing common classical planning algorithms. ",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/juliusarolovitch/Amenable-PDDL",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pddl",
        "lark-parser",
        "typing-extensions",
    ],
)
