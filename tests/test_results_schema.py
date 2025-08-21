import json, os
from jsonschema import validate

SCHEMA = json.load(open(os.path.join(os.path.dirname(__file__), '../docs/rtsc_results.schema.json')))

def test_results_schema():
    demo_file = os.path.join(os.path.dirname(__file__), '../examples/demo_run/rtsc_results.sample.json')
    assert os.path.exists(demo_file)
    data = json.load(open(demo_file))
    validate(instance=data, schema=SCHEMA)
    # Validate the new schema structure
    assert 'results' in data
    assert 'Tc_K' in data['results']
    assert isinstance(data['results']['Tc_K'], (int, float))
    assert data['status'] == 'ok'
