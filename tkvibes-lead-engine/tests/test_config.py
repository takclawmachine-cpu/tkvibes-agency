"""
TKVibes — Config Loader Tests
"""
import os
import copy
import tempfile
import yaml
import pytest
from src.config import load_config


SAMPLE_VALID_CONFIG = {
    "run": {
        "collect_personal_data": False,
        "cache_stale_days": 30,
        "max_leads_per_run": 40,
    },
    "sources": {
        "google_places": True,
    },
    "targets": {
        "cities": ["Delhi", "Mumbai"],
        "categories": ["dental clinic", "lawyer"],
        "max_results_per_query": 60,
    },
    "scoring": {
        "high_fit_categories": ["dental clinic", "dentist"],
        "hot_threshold": 70,
        "warm_threshold": 45,
    },
    "sheets": {
        "worksheet_name": "Leads",
    },
    "handoff": {
        "export_json": "data/leads_export.json",
        "min_tier": "WARM",
    },
}


@pytest.fixture
def valid_config_path():
    """Fixture: write SAMPLE_VALID_CONFIG to a temp file."""
    cfg = copy.deepcopy(SAMPLE_VALID_CONFIG)
    fd, path = tempfile.mkstemp(suffix=".yaml")
    os.close(fd)
    with open(path, "w") as f:
        yaml.dump(cfg, f)
    yield path
    os.unlink(path)


class TestConfigLoad:
    def test_loads_valid_config(self, valid_config_path):
        cfg = load_config(valid_config_path)
        assert isinstance(cfg, dict)
        assert cfg["run"]["max_leads_per_run"] == 40
        assert len(cfg["targets"]["cities"]) == 2

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_config("/tmp/nonexistent_config_xyz.yaml")

    def test_invalid_yaml(self):
        fd, path = tempfile.mkstemp(suffix=".yaml")
        os.close(fd)
        with open(path, "w") as f:
            f.write("{{invalid yaml: [broken}}")
        with pytest.raises(ValueError, match="Invalid YAML"):
            load_config(path)
        os.unlink(path)

    def test_not_a_dict(self):
        fd, path = tempfile.mkstemp(suffix=".yaml")
        os.close(fd)
        with open(path, "w") as f:
            yaml.dump(["just", "a", "list"], f)
        with pytest.raises(ValueError, match="must be a dictionary"):
            load_config(path)
        os.unlink(path)

    def test_missing_required_section(self):
        cfg = {"run": {"collect_personal_data": True, "cache_stale_days": 30, "max_leads_per_run": 10}}
        fd, path = tempfile.mkstemp(suffix=".yaml")
        os.close(fd)
        with open(path, "w") as f:
            yaml.dump(cfg, f)
        with pytest.raises(ValueError, match="Missing required config section"):
            load_config(path)
        os.unlink(path)

    def test_missing_required_key(self):
        cfg = copy.deepcopy(SAMPLE_VALID_CONFIG)
        del cfg["run"]["max_leads_per_run"]
        fd, path = tempfile.mkstemp(suffix=".yaml")
        os.close(fd)
        with open(path, "w") as f:
            yaml.dump(cfg, f)
        with pytest.raises(ValueError, match="Missing required config key.*max_leads_per_run"):
            load_config(path)
        os.unlink(path)

    def test_empty_cities_raises(self):
        cfg = copy.deepcopy(SAMPLE_VALID_CONFIG)
        cfg["targets"]["cities"] = []
        fd, path = tempfile.mkstemp(suffix=".yaml")
        os.close(fd)
        with open(path, "w") as f:
            yaml.dump(cfg, f)
        with pytest.raises(ValueError, match="must have at least one city"):
            load_config(path)
        os.unlink(path)

    def test_empty_categories_raises(self):
        cfg = copy.deepcopy(SAMPLE_VALID_CONFIG)
        cfg["targets"]["categories"] = []
        fd, path = tempfile.mkstemp(suffix=".yaml")
        os.close(fd)
        with open(path, "w") as f:
            yaml.dump(cfg, f)
        with pytest.raises(ValueError, match="must have at least one category"):
            load_config(path)
        os.unlink(path)