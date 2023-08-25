from setuptools import find_packages, setup

__version__ = '0.1.0'

install_requires = [
    'numpy',
    'openai',
    'tenacity',
    'tiktoken',
    'colorama',
    'gradio',
    'langchain @ git+https://github.com/Hallimede/langchain.git#subdirectory=libs/langchain',
    'duckduckgo-search',
    'wikipedia',
    'arxiv',
]

test_requires = [
    'pytest',
    'pytest-cov',
]

dev_requires = [
    'yapf',
    'isort',
    'flake8',
    'pre-commit',
]

setup(
    name='wada',
    version=__version__,
    install_requires=install_requires,
    extras_require={
        'test': test_requires,
        'dev': dev_requires,
    },
    packages=find_packages(),
)
