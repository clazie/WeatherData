import os

os.system("python -m flake8")
os.system("coverage run -m pytest")
os.system("coverage report")
os.system("coverage html")
