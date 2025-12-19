from setuptools import setup, find_packages

setup(
    name='kg_agent',
    version='0.1.0',
    description='KG-Agent: Autonomous agent framework for reasoning over knowledge graphs (skeleton).',
    packages=find_packages(exclude=('tests', 'examples')),
    install_requires=[
        'torch>=2.0.0',
        'transformers>=4.30.0',
        'rdflib>=6.0.0',
        'networkx>=3.0',
        'numpy>=1.24.0'
    ],
    python_requires='>=3.10'
)
