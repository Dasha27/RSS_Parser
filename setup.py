from setuptools import setup
from rss_reader import VERSION

setup(
    name='rss_reader',
    version=f'{VERSION}',
    packages=['rss_reader'],
    url='https://git.epam.com/darya_chernobay/rss_reader',
    license='MIT',
    author='Darya Chernobay',
    author_email='Darya_Chernobay@epam.com',
    description='Pure Python command-line RSS reader',
    entry_points={'console_scripts': [
        'rss_reader = rss_reader.__main__:main',
    ],
    },
)
