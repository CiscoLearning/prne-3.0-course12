from setuptools import setup, find_packages

setup(
    name="te-wrapper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "certifi==2025.1.31",
        "charset-normalizer==3.4.1",
        "idna==3.10",
        "python-dotenv==1.1.0",
        "requests==2.32.3",
        "urllib3==2.4.0"
    ],
)
