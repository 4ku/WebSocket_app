from setuptools import setup, find_packages

setup(
    name='client',
    version='0.1',
    description='WebSocket client',
    author='Ivan Efremov',
    author_email='ef.i.a@ya.ru',
    packages=['.'],
    install_requires=['websockets==10.4']
)