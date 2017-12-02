"""
Setup file for utils library.
"""
from setuptools import setup
from pip.req import parse_requirements

FULL_REQUIREMENTS = []
"""
Holds all requirements which are specified by get_requirements().
"""


def get_requirements(file):
    """
    Reads the requirements.txt and parses the needed
    dependencies and returns them as an array.

    Returns
    -------
        An array of dependencies.
    """

    install_reqs = parse_requirements(file, session="r")
    install_reqs_list = [str(ir.req) for ir in install_reqs]
    FULL_REQUIREMENTS.extend(install_reqs_list)
    return install_reqs


setup(
    name="bp-flugsimulator-utils",
    description="Utils for the bp-flugsimulator",
    version="1.0",
    scripts=[],
    url="https://github.com/bp-flugsimulator/utils",
    author="bp-flugsimulator",
    license="MIT",
    install_requires=get_requirements("requirements.txt"),
    python_requires=">=3.4",
    py_modules=["rpc", "rpc_extra", "status"],
    packages=["utils"],
    extra_requires={
        "websockets": get_requirements("requirements_websockets.txt")
    },
    tests_require=FULL_REQUIREMENTS,
)
