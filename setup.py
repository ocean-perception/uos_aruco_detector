import os
import codecs
import os.path

from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.install import install

classifiers = [
    "Development Status :: 2 - Pre-Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Topic :: Scientific/Engineering",
    "Topic :: Software Development",
]


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


def try_download_configuration_file():
    """Download configuration file if it does not exist."""
    home_dir = os.getenv("HOME")
    configuration_file = (
        home_dir + "/uos_aruco_detector/configuration/configuration.yaml"
    )
    if os.path.exists(configuration_file):
        os.system(
            "wget https://raw.githubusercontent.com/ocean-perception/uos_aruco_detector/main/src/uos_aruco_detector/configuration/configuration.yaml -O {}".format(
                configuration_file
            )
        )


class PostDevelopCommand(develop):
    """Post-installation for development mode."""

    def run(self):
        develop.run(self)
        try_download_configuration_file()


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        install.run(self)
        try_download_configuration_file()


def run_setup():
    """Get version from git, then install."""
    # load long description from README.md
    readme_file = "README.md"
    if os.path.exists(readme_file):
        long_description = open(readme_file, encoding="utf-8", errors="ignore").read()
    else:
        print("Could not find readme file to extract long_description.")
        long_description = ""
    setup(
        name="uos_aruco_detector",
        version=get_version("src/uos_aruco_detector/version.py"),
        install_requires=[
            "pyyaml==6.0",
            "pandas==1.4.2",
            "numpy==1.23.4",
            "matplotlib==3.5.1",
            "scipy==1.8.0",
            "opencv-contrib-python==4.5.5.62",
            "libblas-dev==3.9.0-3",
            "liblapack-dev==3.9.0-3",
            "libatlas-base-dev==3.10.3",
            "libhdf5-dev==1.10.6+repack-4+deb11u1",
        ],
        cmdclass={
            "develop": PostDevelopCommand,
            "install": PostInstallCommand,
        },
        author="Ocean Perception - University of Southampton",
        author_email="miquel.massot-campos@soton.ac.uk; b.thornton@soton.ac.uk",
        description="Aruco marker external localisation system using OpenCV capture",  # noqa
        long_description=long_description,
        url="https://github.com/ocean-perception/uos_aruco_detector",
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        classifiers=classifiers,
        license="BSD",
        entry_points={  # Optional
            "console_scripts": [
                "uos_aruco_detector = uos_aruco_detector.aruco_localisation:main",
                "uos_aruco_detector_client = uos_aruco_detector.client_example:main",
                "uos_aruco_camera_calibration = uos_aruco_detector.camera_calibration:main",
            ],
        },
        include_package_data=True,
        package_data={
            "uos_aruco_detector": [
                "src/uos_aruco_detector/configuration/*.yaml",
            ]
        },
    )


if __name__ == "__main__":
    run_setup()
