import json
import pathlib
from jsonschema import validate


def test_tc_demo_json_matches_schema():
    schema_path = pathlib.Path("schemas") / "ad-screen-1.schema.json"
    data_path = pathlib.Path("examples/validation_runs/tc_demo.json")
    schema = json.loads(schema_path.read_text())
    data = json.loads(data_path.read_text())
    validate(instance=data, schema=schema)
