""" run only once to create the databases """

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = (CURRENT_DIR / ".." / "..").resolve()


# create archive directory
def create_archive_directory():
    from specatalog.main import  BASE_PATH, MOLECULES_PATH, MEASUREMENTS_PATH
    import os
    import shutil

    try:
        os.makedirs(BASE_PATH / MOLECULES_PATH, exist_ok=True)
        print(f"Molecules folder created. at {BASE_PATH} / {MOLECULES_PATH}")

        os.makedirs(BASE_PATH / MEASUREMENTS_PATH, exist_ok=True)
        print(f"Measurements folder created. at {BASE_PATH} / {MEASUREMENTS_PATH}")
    except Exception as e:
        print(f"Directory could not be created: {e}.")
        return False

    try:
        shutil.copy(CURRENT_DIR / "allowed_values_not_adapted.py", BASE_PATH / "allowed_values.py")
        print(f"{BASE_PATH / 'allowed_values.py'} created.")
    except Exception as e:
        print(f"allowed_values.py could not be created: {e}.")
        return False

    return True

def create_database():
    # create database
    try:
        from specatalog.main import engine, BASE_PATH
        from specatalog.models.base import Model
        Model.metadata.create_all(engine)
        print(f"Database created at {BASE_PATH}")
        return True
    except Exception as e:
        print(f"Database could not be created: {e}.")
        return False



def specatalog_init_db():
    from specatalog.main import BASE_PATH
    exist = input(f"Does the archive and database already exist at {BASE_PATH}? y/n?")

    if exist == "n":
        create_archive_directory()
        create_database()

    else:
        print("No new archive created.")
