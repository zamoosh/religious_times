from setuptools import setup, find_packages

# Read the content of README.md for the long description
with open('README.md', 'r', encoding='utf-8') as file:
    long_description = file.read()

setup(
    name='religious_times',
    version='2.4',
    author='zamoosh',
    description='A library to calculate `pray times` for muslims.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/zamoosh/religious_times/',
    packages=find_packages(),
    install_requires=[],
    license='MIT',
    keywords='pray, muslim, prayer, fajr, imsak, sunrise, duhr, asr, sunset, maghrib, isha, midnight, religious times, shia',
)
