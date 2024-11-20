from setuptools import setup

setup(
    name="hello-pyqt",
    version="0.1.0",
    py_modules=["main", "vision_assistant", "response_models", "tutor_view"],
    install_requires=[
        "PyQt5",
        "anthropic[bedrock,vertex]>=0.37.1",
        "pillow",
    ],
    entry_points={
        "console_scripts": [
            "hello-pyqt=main:main",
        ],
    },
)
from setuptools import setup, find_packages

setup(
    name="vision-assistant",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "PyQt5",
        "anthropic",
        "Pillow",
    ],
    python_requires=">=3.8",
)
