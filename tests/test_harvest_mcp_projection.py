"""Human harvest controls never become executable MCP tools by catalog generation."""
from app.core.screen_definitions_harvest_controls import COMMAND_PATHS, build_harvest_controls
from scripts.generate_mcp_mask_action_map import build_map


def test_all_harvest_writes_are_explicitly_blocked_without_tool_identity():
    actions={a['key']:a for a in build_harvest_controls()['actions']}
    mapping={a['mask_action_id']:a for a in build_map()['mappings']}
    for key,path in COMMAND_PATHS.items():
        assert actions[key]['forbiddenForAgents'] is True
        entry=mapping['mask:agrar/harvest-controls:'+key]
        assert entry['coverage']=='blocked_human_only'
        assert entry['mcp_tool_id'] is None
        assert entry['command_endpoint']==path
    assert len(COMMAND_PATHS)==8


def test_mapping_summary_reports_actual_remaining_counts():
    data=build_map()
    for category in ['open_high','open_medium','blocked_human_only']:
        assert f"{category} {data['stats']['by_coverage'].get(category,0)}" in data['classification_notes']
