from setuptools import find_packages, setup

setup(
    name="backend_neuroland",
    version="0.1.0",
    description="PUTHON DRF API",
    author="Veronika Shakalova",
    author_email="veronika.s@example.com",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django :: 2.2",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=[
        "Django>=2.2,<3.0",
        "djangorestframework>=3.11,<4.0",
        "firebase-admin>=4.5.0,<5.0.0",
    ],
    python_requires=">=3.7",
)
