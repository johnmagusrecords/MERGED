from setuptools import setup, find_packages

setup(
    name="trading-bot",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'python-dotenv>=0.19.0',
        'requests>=2.26.0',
        'pandas>=1.3.0',
        'numpy>=1.21.0',
        'pandas-ta>=0.3.14b'
    ]
)
