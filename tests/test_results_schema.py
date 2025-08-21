import json, os
from jsonschema import validate

SCHEMA = json.load(open(os.path.join(os.path.dirname(__file__), '../docs/rtsc_results.schema.json')))

def test_results_schema():
    demo_file = os.path.join(os.path.dirname(__file__), '../examples/demo_run/rtsc_results.sample.json')
    assert os.path.exists(demo_file)
    data = json.load(open(demo_file))
    validate(instance=data, schema=SCHEMA)
    assert isinstance(data['tc_estimate_K'], (int, float))
    assert isinstance(data['success_probability']['rtsc_300K'], (int, float))
