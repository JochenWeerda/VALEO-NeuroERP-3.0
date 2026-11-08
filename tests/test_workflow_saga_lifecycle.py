"""Real event-loop contracts for the existing standalone workflow coordinator."""
import asyncio
import gc
import importlib.util
from pathlib import Path
import weakref

import pytest

spec = importlib.util.spec_from_file_location('workflow_saga_under_test', Path(__file__).parents[1] / 'services/workflow/app/core/saga.py')
saga = importlib.util.module_from_spec(spec)
spec.loader.exec_module(saga)
pytestmark = pytest.mark.asyncio


async def test_future_step_must_finish_before_following_step_and_completed_status():
    coordinator = saga.SagaCoordinator()
    pending = asyncio.get_running_loop().create_future()
    entered, finished = asyncio.Event(), asyncio.Event()
    def action(context):
        entered.set()
        return pending
    await coordinator.register(saga.SagaDefinition('future', [saga.SagaStep('first', action), saga.SagaStep('last', lambda _: finished.set())]))
    instance = await coordinator.start('future', {})
    await asyncio.wait_for(entered.wait(), 1)
    try:
        assert instance.status == 'running'
        assert instance.completed_steps == []
        assert not finished.is_set()
    finally:
        pending.set_result(None)
    await asyncio.wait_for(finished.wait(), 1)
    await asyncio.sleep(0)
    assert instance.status == 'completed'
    assert instance.completed_steps == ['first', 'last']


async def test_future_compensation_is_awaited_before_reporting_compensated():
    coordinator = saga.SagaCoordinator()
    pending = asyncio.get_running_loop().create_future()
    entered = asyncio.Event()
    def compensate(_):
        entered.set()
        return pending
    def fail(_):
        raise ValueError('synthetic step failure')
    await coordinator.register(saga.SagaDefinition('compensate', [saga.SagaStep('first', lambda _: None, compensate), saga.SagaStep('fail', fail)]))
    instance = await coordinator.start('compensate', {})
    await asyncio.wait_for(entered.wait(), 1)
    try:
        assert instance.status == 'compensating'
    finally:
        pending.set_result(None)
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    assert instance.status == 'compensated'
    assert instance.error == 'synthetic step failure'


async def test_suspended_task_is_retained_until_cancelled_and_then_released():
    coordinator = saga.SagaCoordinator()
    entered = asyncio.Event()
    references = []
    async def wait_forever(_):
        references.append(weakref.ref(asyncio.current_task()))
        entered.set()
        await asyncio.Future()
    await coordinator.register(saga.SagaDefinition('suspended', [saga.SagaStep('wait', wait_forever)]))
    instance = await coordinator.start('suspended', {})
    await asyncio.wait_for(entered.wait(), 1)
    gc.collect()
    task = references[0]()
    assert task is not None, 'Coordinator lost its running background task'
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    await asyncio.sleep(0)
    assert instance.status == 'cancelled'
    del task
    gc.collect()
    assert references[0]() is None


async def test_rejected_compensation_future_is_not_reported_as_success(caplog):
    caplog.set_level('INFO', logger=saga.__name__)
    coordinator = saga.SagaCoordinator()
    compensation = asyncio.get_running_loop().create_future()
    compensation.set_exception(ValueError('synthetic compensation failure'))
    def fail(_):
        raise ValueError('synthetic step failure')
    await coordinator.register(saga.SagaDefinition('rejected', [saga.SagaStep('first', lambda _: None, lambda _: compensation), saga.SagaStep('fail', fail)]))
    instance = await coordinator.start('rejected', {})
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    assert instance.status == 'compensation_failed'
    assert instance.error == 'synthetic step failure'
    assert 'Kompensationsstatus compensation_failed' in caplog.text


async def test_unexpected_background_error_is_observed_and_status_is_failed(caplog):
    coordinator = saga.SagaCoordinator()
    async def broken(_):
        raise RuntimeError('synthetic coordinator failure')
    coordinator._execute = broken
    await coordinator.register(saga.SagaDefinition('unexpected', []))
    instance = await coordinator.start('unexpected', {})
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    assert instance.status == 'failed'
    assert instance.error == 'synthetic coordinator failure'
    assert 'Saga execution failed' in caplog.text
    assert not coordinator._tasks


async def test_synchronous_and_coroutine_steps_remain_ordered_and_tasks_are_released():
    coordinator = saga.SagaCoordinator()
    seen = []
    async def second(_):
        await asyncio.sleep(0)
        seen.append('second')
    await coordinator.register(saga.SagaDefinition('normal', [saga.SagaStep('first', lambda _: seen.append('first')), saga.SagaStep('second', second)]))
    instance = await coordinator.start('normal', {})
    for _ in range(4):
        await asyncio.sleep(0)
    assert seen == ['first','second']
    assert instance.status == 'completed'
    assert not coordinator._tasks


async def test_custom_awaitable_is_awaited_and_status_lookup_stays_live():
    coordinator = saga.SagaCoordinator()
    pending = asyncio.get_running_loop().create_future()
    entered = asyncio.Event()
    class StepResult:
        def __await__(self):
            entered.set()
            return pending.__await__()
    await coordinator.register(saga.SagaDefinition('custom', [saga.SagaStep('wait', lambda _: StepResult())]))
    instance = await coordinator.start('custom', {})
    await asyncio.wait_for(entered.wait(), 1)
    assert (await coordinator.status(instance.id)).status == 'running'
    pending.set_result(None)
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    assert (await coordinator.status(instance.id)).status == 'completed'


async def test_unknown_definition_does_not_start_any_background_work():
    coordinator = saga.SagaCoordinator()
    with pytest.raises(KeyError):
        await coordinator.start('missing', {})
    assert not coordinator._tasks
