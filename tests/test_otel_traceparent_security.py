"""Trace-context parsing stays bounded for untrusted non-HTTP carriers."""
import subprocess
import sys


def test_traceparent_valid_context_and_bounded_rejection():
    code = r'''
from opentelemetry.trace import get_current_span
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

p = TraceContextTextMapPropagator()
valid = '00-0123456789abcdef0123456789abcdef-0123456789abcdef-01'
context = p.extract({'traceparent': valid})
span = get_current_span(context).get_span_context()
assert span.is_valid and span.trace_id == int('0123456789abcdef0123456789abcdef', 16)
assert span.span_id == int('0123456789abcdef', 16)
for value in (valid + ' ' * 200000 + '\r\n', valid + '\r\n', valid + ' ' * 513):
    assert not get_current_span(p.extract({'traceparent': value})).get_span_context().is_valid
'''
    subprocess.run([sys.executable, '-c', code], check=True, timeout=5, capture_output=True, text=True)
