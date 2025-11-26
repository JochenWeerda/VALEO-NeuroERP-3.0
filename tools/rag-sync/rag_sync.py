"""
CLI-Tool zur Synchronisation von Wissensinhalten in die RAG-Pipeline.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import os

import httpx


logger = logging.getLogger("rag_sync")


DEFAULT_EXTENSIONS = (".md", ".mdx", ".txt")


@dataclass
class RAGSyncConfig:
    source_dir: Path = Path("knowledge-base")
    output_file: Optional[Path] = None
    vector_endpoint: Optional[str] = None
    namespace: str = "default"
    embedding_provider: str = "auto"
    embedding_model: str = "text-embedding-3-small"
    batch_size: int = 32
    dry_run: bool = False
    file_extensions: Iterable[str] = field(default_factory=lambda: DEFAULT_EXTENSIONS)


class DocumentLoader:
    def __init__(self, config: RAGSyncConfig) -> None:
        self.config = config

    def load_documents(self) -> List[Dict[str, Any]]:
        documents: List[Dict[str, Any]] = []
        for path in self.config.source_dir.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in self.config.file_extensions:
                continue
            content = path.read_text(encoding="utf-8")
            documents.append(
                {
                    "path": path,
                    "content": content,
                    "relative_path": str(path.relative_to(self.config.source_dir)),
                }
            )
        logger.info("Geladene Dokumente: %s", len(documents))
        return documents


class MarkdownChunker:
    def __init__(self, max_tokens: int = 400) -> None:
        self.max_tokens = max_tokens

    def chunk(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        content = document["content"]
        lines = content.splitlines()
        chunks: List[Dict[str, Any]] = []
        buffer: List[str] = []
        token_count = 0
        current_heading = "root"

        for line in lines:
            if line.startswith("#"):
                if buffer:
                    chunks.append(
                        {
                            "heading": current_heading,
                            "text": "\n".join(buffer).strip(),
                        }
                    )
                    buffer = []
                    token_count = 0
                current_heading = line.lstrip("# ").strip() or "section"
                continue

            buffer.append(line)
            token_count += max(1, len(line.split()))
            if token_count >= self.max_tokens:
                chunks.append(
                    {
                        "heading": current_heading,
                        "text": "\n".join(buffer).strip(),
                    }
                )
                buffer = []
                token_count = 0

        if buffer:
            chunks.append({"heading": current_heading, "text": "\n".join(buffer).strip()})

        enriched_chunks = [
            {
                "document": document["relative_path"],
                "heading": chunk["heading"],
                "text": chunk["text"],
            }
            for chunk in chunks
            if chunk["text"]
        ]
        return enriched_chunks


class HashEmbeddingProvider:
    EMBEDDING_DIM = 64

    def embed(self, text: str) -> List[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        repeated = (digest * ((self.EMBEDDING_DIM // len(digest)) + 1))[: self.EMBEDDING_DIM]
        return [byte / 255 for byte in repeated]


class OpenAIEmbeddingProvider:
    def __init__(self, model: str) -> None:
        self.model = model
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise RuntimeError("openai Paket nicht installiert. Bitte Abhängigkeiten ergänzen.") from exc
        self.client = AsyncOpenAI()

    async def embed(self, text: str) -> List[float]:
        response = await self.client.embeddings.create(model=self.model, input=text)
        return list(response.data[0].embedding)


class VectorStoreClient:
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    async def upsert(self, records: List[Dict[str, Any]]) -> None:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(self.endpoint, json={"records": records})
            response.raise_for_status()


class RAGSync:
    def __init__(self, config: RAGSyncConfig) -> None:
        self.config = config
        self.loader = DocumentLoader(config)
        self.chunker = MarkdownChunker()
        provider = config.embedding_provider
        if provider == "auto":
            provider = "openai" if os.getenv("OPENAI_API_KEY") else "hash"
            logger.info("Automatische Auswahl des Embedding-Providers: %s", provider)

        self.config.embedding_provider = provider

        if provider == "openai":
            self.embedding_provider = OpenAIEmbeddingProvider(config.embedding_model)
        elif provider == "hash":
            self.embedding_provider = HashEmbeddingProvider()
        else:
            raise ValueError(f"Unbekannter Embedding-Provider: {provider}")
        self.vector_client = VectorStoreClient(config.vector_endpoint) if config.vector_endpoint else None

    async def run(self) -> Dict[str, Any]:
        documents = self.loader.load_documents()
        all_chunks: List[Dict[str, Any]] = []

        for document in documents:
            chunks = self.chunker.chunk(document)
            for chunk in chunks:
                embedding = (
                    await self.embedding_provider.embed(chunk["text"])
                    if isinstance(self.embedding_provider, OpenAIEmbeddingProvider)
                    else self.embedding_provider.embed(chunk["text"])
                )
                record = {
                    "id": hashlib.md5(f"{chunk['document']}::{chunk['heading']}::{hashlib.md5(chunk['text'].encode('utf-8')).hexdigest()}".encode("utf-8")).hexdigest(),  # noqa: S324
                    "text": chunk["text"],
                    "metadata": {
                        "document": chunk["document"],
                        "heading": chunk["heading"],
                        "namespace": self.config.namespace,
                    },
                    "embedding": embedding,
                }
                all_chunks.append(record)

        if self.config.output_file:
            self.config.output_file.parent.mkdir(parents=True, exist_ok=True)
            self.config.output_file.write_text(json.dumps(all_chunks, indent=2), encoding="utf-8")
            logger.info("Lokaler Export nach %s abgeschlossen", self.config.output_file)

        if self.vector_client and not self.config.dry_run:
            for start in range(0, len(all_chunks), self.config.batch_size):
                batch = all_chunks[start : start + self.config.batch_size]
                await self.vector_client.upsert(batch)
            logger.info("Vector Store Upsert abgeschlossen (%s Einträge)", len(all_chunks))

        return {"documents": len(documents), "chunks": len(all_chunks)}


def parse_args() -> RAGSyncConfig:
    parser = argparse.ArgumentParser(description="Synchronisiere Wissensdokumente in die RAG-Pipeline.")
    parser.add_argument("--source", type=Path, default=Path("knowledge-base"), help="Quellverzeichnis für Dokumente.")
    parser.add_argument("--output", type=Path, help="Optionale JSON-Ausgabedatei.")
    parser.add_argument("--endpoint", type=str, help="Optionaler HTTP-Endpunkt für Vector-Store Upserts.")
    parser.add_argument("--namespace", type=str, default="default", help="Namespace für Embeddings.")
    parser.add_argument("--embedding-provider", choices=["hash", "openai", "auto"], default="auto")
    parser.add_argument("--embedding-model", type=str, default="text-embedding-3-small")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--dry-run", action="store_true", help="Kein Upsert, nur Analyse/Ausgabe.")
    parser.add_argument("--verbose", action="store_true", help="Verbose Logging.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if not args.verbose else logging.DEBUG)

    return RAGSyncConfig(
        source_dir=args.source,
        output_file=args.output,
        vector_endpoint=args.endpoint,
        namespace=args.namespace,
        embedding_provider=args.embedding_provider,
        embedding_model=args.embedding_model,
        batch_size=args.batch_size,
        dry_run=args.dry_run,
    )


def main() -> None:
    config = parse_args()
    sync = RAGSync(config)
    result = asyncio.run(sync.run())
    logger.info("Sync abgeschlossen: %s", result)


if __name__ == "__main__":
    main()


