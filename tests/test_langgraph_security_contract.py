"""Herstellerfix-Vertraege ohne externen Dienst oder Datenbank."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from langgraph.store.base import GetOp, ListNamespacesOp, MatchCondition, PutOp, SearchOp
from langgraph.store.sqlite.base import SqliteStore, _group_ops
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph
from langgraph_sdk._async.stream import AsyncThreadStream, _AgentModule
from langgraph_sdk._sync.stream import SyncThreadStream, _SyncAgentModule


def test_sdk_sync_paths_encode_identifiers():
    http = SimpleNamespace(get=Mock(return_value={}))
    owner = SimpleNamespace(_closed=False, _headers={}, assistant_id='agent/blue?view=1', thread_id='thread/blue?view=1', _http=http)
    _SyncAgentModule(owner).get_tree()
    SyncThreadStream._fetch_state(owner)
    assert [call.args[0] for call in http.get.call_args_list] == [
        '/assistants/agent%2Fblue%3Fview%3D1/graph', '/threads/thread%2Fblue%3Fview%3D1/state']


def test_sdk_async_paths_encode_identifiers():
    http = SimpleNamespace(get=AsyncMock(return_value={}))
    owner = SimpleNamespace(_closed=False, _headers={}, assistant_id='agent/blue?view=1', thread_id='thread/blue?view=1', _http=http)
    async def exercise():
        await _AgentModule(owner).get_tree()
        await AsyncThreadStream._fetch_state(owner)
    asyncio.run(exercise())
    assert [call.args[0] for call in http.get.call_args_list] == [
        '/assistants/agent%2Fblue%3Fview%3D1/graph', '/threads/thread%2Fblue%3Fview%3D1/state']


@pytest.mark.parametrize('operation', [GetOp(('tenant.user',), 'key'), SearchOp(('tenant.user',)),
    PutOp(('tenant.user',), 'key', {'value': 1}),
    ListNamespacesOp(match_conditions=(MatchCondition('prefix', ('tenant.user',)),))])
def test_sqlite_store_rejects_ambiguous_namespace_before_io(operation):
    store = object.__new__(SqliteStore)
    with pytest.raises(ValueError):
        store.batch([operation])


def test_sqlite_valid_namespace_is_accepted_by_real_batch_guard():
    grouped, count = _group_ops([GetOp(('tenant', 'user'), 'key')])
    assert count == 1 and GetOp in grouped


def test_graph_compiles_with_real_sqlite_saver_without_database_io():
    saver = SqliteSaver(Mock())
    graph = StateGraph(dict)
    graph.add_node('example', lambda state: state)
    graph.set_entry_point('example')
    graph.add_edge('example', END)
    assert graph.compile(checkpointer=saver).checkpointer is saver
