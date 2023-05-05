FROM python:3.11

ADD NexusModSorter.py .

run pip install requests beautifulsoup4 python-dotenv

CMD ["python", "NexusModSorter.py"]