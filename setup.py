from setuptools import setup, find_packages

setup(
    name="gerenciador_faturas",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'customtkinter',
        'tkcalendar',
        'Pillow',
        'matplotlib',
        'sqlite3',
    ],
    python_requires='>=3.6',
) 