from pathlib import Path


def test_docflow_conversion_inserts_target_header_before_fk_link():
    source = Path("app/services/docflow_service.py").read_text(encoding="utf-8")
    convert_block = source[source.index("    def convert("):source.index("    def post_document(")]

    target_header = convert_block.index("INSERT INTO domain_docflow.document_headers")
    header_link = convert_block.index("INSERT INTO domain_docflow.document_header_links")

    assert target_header < header_link
