from pathlib import Path
import pytest, os, uuid, shutil

from smc.models.base import init_db


@pytest.fixture()
def client():
    tempdir = Path("/tmp") / str(uuid.uuid4())

    try:
        tempdir.mkdir()
        shutil.copyfile(
            Path(__file__).parent / "resources/smc.db", str(Path(tempdir) / "smc.db")
        )
        init_db(str(Path(tempdir) / "smc.db"))

        from smc.api import app
        from smc.config import DAO_SETTINGS, _ROOT_DIR

        externaldb = _ROOT_DIR / "../data/home/databases"
        for cfg in DAO_SETTINGS.values():
            cfg["args"]["dbfile"] = os.path.join(
                externaldb, Path(cfg["args"]["dbfile"]).name
            )
            assert os.path.exists(cfg["args"]["dbfile"]), cfg["args"]["dbfile"]
            cfg["args"]["proxy"] = False

        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client
    finally:
        if tempdir.exists():
            shutil.rmtree(tempdir, ignore_errors=True)
