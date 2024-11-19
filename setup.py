from setuptools import setup

setup(
    name="hello-pyqt",
    version="0.1.0",
    py_modules=["main"],
    install_requires=[
        "PyQt5",
    ],
    entry_points={
        "console_scripts": [
            "hello-pyqt=main:main",
        ],
    },
)
