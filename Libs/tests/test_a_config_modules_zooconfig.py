import ast
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[2]

CONFIG_ONLY_MODULES = (
    "KUMA.py",
    "MultiCrystal.py",
    "Libs/CryImageProc.py",
    "Libs/AttFactor.py",
    "Libs/BeamsizeConfig.py",
    "Libs/ESA.py",
    "Libs/RasterSchedule.py",
    "Libs/ScheduleBSS.py",
    "Libs/UserESA.py",
    "Libs/BSSconfig41.py",
)


@pytest.mark.parametrize("relative_path", CONFIG_ONLY_MODULES)
def test_config_only_module_delegates_ini_loading_to_zooconfig(relative_path):
    path = ROOT / relative_path
    source = path.read_text()
    tree = ast.parse(source, filename=str(path))

    load_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "ZooConfig"
        and node.func.attr == "load_config"
    ]

    assert load_calls, f"{relative_path} does not delegate config loading"
    assert "os.environ['ZOOCONFIGPATH']" not in source
    assert 'os.environ["ZOOCONFIGPATH"]' not in source
    assert "ConfigParser(" not in source
