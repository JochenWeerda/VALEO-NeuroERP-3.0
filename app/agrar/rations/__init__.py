"""Rationsoptimierung - modular aufgebaut (Refactor 2026-04-23).

Historisch war der gesamte Code in
`app/api/v1/endpoints/rations_optimization.py` zusammengefasst (~6000
Zeilen). Diese Refactoring-Phase zerlegt ihn in logisch gekapselte
Module ohne Verhaltensaenderung. Die Endpoint-Datei bleibt weiterhin
Single Source of Truth fuer die Pydantic-Request-Modelle und die
FastAPI-Routen; sie importiert die Bausteine von hier.

Schichten:
  constants/        -> fachliche Konstanten (DLG 01|25, GfE-2023, Weide)
  compound_feed/    -> OCR/PDF-Parsing + Etikettenauswertung
  repository/       -> DLG-JSON-Loader + Caching
  http/             -> Proxy-Hilfen fuer Remote-Rations-Service
  solver/           -> LP-Formulierung, Constraint-Registry, Relaxation
  response/         -> Response-Builder + Aggregationen
"""
