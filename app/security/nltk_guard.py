"""NLTK runtime download guard.

Prevents nltk.download() from being called at runtime in production.
NLTK data must be pre-loaded during the build process and shipped read-only.
NLTK_DATA env var should point to a read-only directory.
"""


def disable_nltk_runtime_downloads() -> None:
    """Block nltk.download() calls at runtime. Call once at app startup."""
    try:
        import nltk

        def _blocked_download(*args, **kwargs):  # type: ignore[no-untyped-def]
            raise RuntimeError(
                "nltk.download() is disabled at runtime. "
                "Pre-load NLTK corpora during the Docker build step "
                "and set NLTK_DATA to a read-only directory."
            )

        nltk.download = _blocked_download
    except ImportError:
        pass
