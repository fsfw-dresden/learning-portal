from setuptools import setup

setup(
    name="hello-pyqt",
    version="0.1.0",
    py_modules=["main", "vision_assistant", "response_models"],
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
