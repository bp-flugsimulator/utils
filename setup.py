"""
Setup file for utils library.
"""
from setuptools import setup
from pip.req import parse_requirements


def get_requirements():
    """
    Reads the requirements.txt and parses the needed
    dependencies and returns them as an array.

    Returns
    -------
        An array of dependencies.
    """

    install_reqs = parse_requirements("requirements.txt", session="r")
    return [str(ir.req) for ir in install_reqs]


setup(
    name="bp-flugsimulator-utils",
    description="Utils for the bp-flugsimulator",
    version="1.0",
    scripts=[],
    url="https://github.com/bp-flugsimulator/utils",
    author="bp-flugsimulator",
    license="MIT",
    install_requires=get_requirements(),
    python_requiers=">=3.4",
    py_modules=["rpc", "status"],
    packages=["utils"],
)
