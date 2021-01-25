import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="asyncio-gsm-modem-sinusoidal",
    version="0.0.1",
    author="sinusoidal",
    author_email="",
    description="An asyncio GSM modem driver library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sinusoidal36/asyncio-gsm-modem",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['pyserial-asyncio', 'smspdudecoder']
)