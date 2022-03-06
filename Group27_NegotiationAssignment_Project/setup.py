from setuptools import setup


# provide the name of your agent in snake_case below
# the directory containing the agent Python files should have the same name
NAME = "Group27_NegotiationAssignment_Agent"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name=NAME,
    version="1.1.4",  # version corresponding with geniusweb version
    author="Group 27 - Atanas Pashov, Ivan Stranski, Marko Ivanov, Stoyan Dimitrov",  # add the names of your project group members
    description="Agent that offers bids based on opponent modelling until an agreement is reached.",  # give a short description of your agent
    long_description=long_description,  # the `README.md` file serves as a long description
    install_requires=[
        "geniusweb@https://tracinsy.ewi.tudelft.nl/pubtrac/GeniusWebPython/export/83/geniuswebcore/dist/geniusweb-1.1.4.tar.gz",
        "numpy",  # not required, but in support of the example
    ],
    py_modules=["party"],  # to include the `party.py` file
    packages=[NAME],  # name of the directory with the agent files
    python_requires=">=3.9,<3.10",
)
