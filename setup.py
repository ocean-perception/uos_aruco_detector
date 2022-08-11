import os
import os.path

from setuptools import find_packages, setup

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
        version="1.0.3",
        install_requires=[
            "PyYAML",
            "pandas",
            "numpy",
            "matplotlib",
            "opencv-python",
            "opencv-contrib-python",
        ],
        author="Ocean Perception - University of Southampton",
        author_email="miquel.massot-campos@soton.ac.uk",
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
