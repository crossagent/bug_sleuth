from setuptools import setup, find_packages

setup(
    name="bug_sleuth",
    version="0.1.0",
    description="Automated Bug Analysis and Reproduction Agent",
    packages=find_packages(),  # Automatically finds 'agents', 'shared_libraries'
    install_requires=[
        "google-adk",
        "google-genai",
        "uvicorn",
        "fastapi"
    ],
    python_requires=">=3.10",
)
