import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="async-gsm-modem",
    version="0.0.1",
    author="sinusoidal",
    author_email="",
    description="An async GSM modem driver library",
    keywords=['gsm','modem','asyncio','async','lte','sms','text','usb','serial','phone','mobile','messaging'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sinusoidal36/async-gsm-modem",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['pyserial-asyncio', 'smspdudecoder']
)