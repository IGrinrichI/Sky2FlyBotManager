import os

from setuptools import setup
from Cython.Build import cythonize


def get_ext_paths(directory):
    paths = []
    for filename in os.listdir(directory):
        if filename.endswith(".py") and not filename.startswith("__"):
            paths.append(os.path.join(directory, filename))
    return paths


files = ["app.py", "player.py", "exceptions.py", "ram_cleaner.py", "app_logger.py", "farm_process.py", "licence.py", "clients_widget.py", "presets_widget.py"] + get_ext_paths('..\Clicker')
setup(ext_modules=cythonize(files, compiler_directives={'language_level': "3"}))
