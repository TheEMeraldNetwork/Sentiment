from setuptools import setup, find_packages

setup(
    name="sentiment_analysis",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'transformers',
        'finnhub-python',
        'yfinance',
        'tabulate'
    ]
) 