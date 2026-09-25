"""Check standalone config loading without importing or running device code."""

import ast
from pathlib import Path

import pytest

from Libs import ZooConfig


@pytest.mark.parametrize("filename", ["CCDlen.py", "PreColli.py"])
def test_main_config_assignment_delegates_to_loader(filename, monkeypatch, tmp_path):
    path = Path(__file__).parents[1] / filename
    tree = ast.parse(path.read_text(), filename=str(path))
    main = next(
        node for node in tree.body
        if isinstance(node, ast.If)
        and ast.unparse(node.test) == "__name__ == '__main__'"
    )
    assignment = next(
        node for node in main.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "config"
                for target in node.targets)
    )
    tmp_path.joinpath("beamline.ini").write_text("[beamline]\nbeamline = BLTEST\n")
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    calls = []
    real_load = ZooConfig.load_config

    def load_config():
        calls.append("load")
        return real_load()

    monkeypatch.setattr(ZooConfig, "load_config", load_config)
    namespace = {"ZooConfig": ZooConfig}
    # Execute only the config assignment: never imports, initDevice or sockets.
    fragment = ast.Module(body=[assignment], type_ignores=[])
    exec(compile(fragment, str(path), "exec"), namespace)

    assert calls == ["load"]
    assert namespace["config"].get("beamline", "beamline") == "BLTEST"
