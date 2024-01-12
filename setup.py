from setuptools import setup, find_packages

setup(
    name='Atlas',
    version='0.1.0',
    author='Nick Tolhurst',
    author_email='nicholastolhurst@outlook.com',
    description='A voice assistant project',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'aiofiles',
        'loguru',
        'SpeechRecognition',
        'python-dotenv',
        'pygame',
        'pyaudio'
    ],
    python_requires='>=3.6',  # Minimum version requirement of the Python interpreter
    entry_points={
        'console_scripts': [
            'atlas=atlas.main:main',  # Change 'main:main' to point to your application's entry function
        ],
    },
)