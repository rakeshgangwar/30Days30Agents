from setuptools import setup, find_packages

setup(
    name="task-automation-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic-ai",
        "pydantic",
        "requests",
        "python-dotenv",
        "streamlit",
    ],
    author="SJLabs",
    author_email="example@example.com",
    description="Task Automation Agent using PydanticAI and Beehive",
    keywords="automation, agent, pydantic-ai, beehive",
    python_requires=">=3.9",
)
