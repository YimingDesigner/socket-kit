from setuptools import setup, find_packages

setup(
    name="socket_kit",
    version="0.2.1",
    description="A utility with concise and more fluent code in socket programming",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Yiming Liu",
    author_email="YimingDesigner@gmail.com",
    package_dir={'':"src"},
    packages=find_packages("src"),
    install_requires=[
        "numpy",
        "opencv-python",
        "mysql-connector-python",
    ],
)