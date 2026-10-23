"""Exercise the patched OTel cohort together; no exporter network or PostgreSQL writes."""
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter


def test_fastapi_and_sql_spans_survive_patched_cohort():
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    engine = create_engine('sqlite://', poolclass=StaticPool, connect_args={'check_same_thread': False})
    app = FastAPI()

    @app.get('/probe')
    def probe():
        with engine.connect() as connection:
            return {'value': connection.execute(text('select 1')).scalar_one()}

    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
    instrumentor = SQLAlchemyInstrumentor()
    instrumentor.instrument(engine=engine, tracer_provider=provider)
    try:
        with TestClient(app) as client:
            assert client.get('/probe').json() == {'value': 1}
        spans = exporter.get_finished_spans()
        assert any(span.attributes.get('http.route') == '/probe' for span in spans)
        assert any(span.attributes.get('db.statement') == 'select 1' for span in spans)
    finally:
        instrumentor.uninstrument()
        FastAPIInstrumentor.uninstrument_app(app)
        engine.dispose()
        provider.shutdown()
