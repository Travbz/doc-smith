from setuptools import setup, find_packages

setup(
    name="docsmith",
    packages=find_packages(),
    install_requires=[
        'openai>=1.0.0',
        'gitpython>=3.1.40',
        'PyGithub>=2.1.1',
        'python-dotenv>=1.0.0',
        'aiohttp>=3.9.1',
        'tiktoken>=0.5.1',
        'rich>=13.7.0',
    ],
)