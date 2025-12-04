import sqlalchemy as alc
import sqlalchemy.orm as orm
import json
from pathlib import Path
import shutil
from importlib.resources import files

home_defaults = Path.home() / ".specatalog" / "defaults.json"
if not home_defaults.exists():
    home_defaults.parent.mkdir(exist_ok=True)
    shutil.copy(files("specatalog.user") / "defaults.json", home_defaults)

with home_defaults.open("r") as f:
    defaults = json.load(f)

# set path defintions
BASE_PATH = Path(defaults["base_path"]).resolve()
MEASUREMENTS_PATH = Path("data")
MOLECULES_PATH = Path("molecules")

# initialise engine
engine = alc.create_engine(f"sqlite:///{BASE_PATH}/specatalog.db", echo=True)

# initialise session and connect to engine
Session = orm.scoped_session(
    orm.sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine
        )
    )

# parameter fo the initalisation of new sqlite engines
@alc.event.listens_for(alc.Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
