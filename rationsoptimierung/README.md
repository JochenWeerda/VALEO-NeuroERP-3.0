# VALEO Rations Optimization Tool

A production-ready, modular ration optimization tool for dairy cattle that uses linear optimization to minimize feed costs while meeting nutritional requirements. Designed for integration with the VALEO ERP Agrarportal.

## Overview

This tool implements a least-cost ration formulation system for dairy cows using linear programming. It calculates optimal feed combinations that meet nutritional requirements at minimum cost, following GfE-2023 guidelines for energy (ME basis) and protein (SIDP basis).

## Features

- **Linear Optimization**: Uses PuLP solver for least-cost ration formulation
- **Modular Architecture**: Clean separation of concerns (domain, services, API, optimization)
- **API-First Design**: RESTful API with comprehensive OpenAPI documentation
- **Validation**: Comprehensive input validation with meaningful error messages
- **Extensible**: Easy to add new feed types, constraints, or objectives
- **Docker Ready**: Containerized for easy deployment
- **Test Coverage**: Comprehensive test suite
- **ERP Integration Ready**: Designed for later integration with VALEO ERP

## Technical Specifications

### Target Animal
- Holstein high-performance dairy cows

### Optimization Approach
- **Objective**: Minimize feed cost per cow per day
- **Method**: Linear programming (Least-Cost Ration)
- **Solver**: PuLP with CBC solver (configurable)
- **Decision Variables**: kg dry matter per feed per cow per day

### Nutritional Framework (GfE-2023-aligned)
- **Energy**: Metabolizable Energy (ME) basis – Erhaltung **0,64 MJ/kg LM^0,75**; Milch über **ECM** und **ME/ECM ≈ 3,15/0,66** (siehe Code `app/nutrition/gfe2023.py`). **NEL ≠ ME** (keine 1:1-Substitution; Futtermittel-ME aus eigener ME-Bewertung).
- **Protein**: Small Intestine Digestible Protein (SIDP) basis (Näherung Erhaltung + Milchprotein)
- **Fiber**: Ash-Neutral Detergent Fiber Organic Matter (aNDFom)
- **Expandable**: Designed for future addition of SIDAA, OMD, RMD
- **Hinweis**: Vollständige Tabellen (sidAA, FAN-Korrekturen, exakte Mineralien) nur in der GfE-Publikation (DLG-Verlag); das Modul spiegelt die in Fachartikeln konsistent genannten ME-/ECM-Kernelemente wider.
- **Futtermittel-ME (Praxis)**: Referenz-CSVs **DLG Futterwerttabellen Wiederkäuer 2025** und **LKV Sachsen Getreideernte 2025** unter `data/reference/`; Einordnung und Mapping → `FeedIngredient` in **`docs/futterwerte_dlg_2025_gfe2023.md`**. Getreide ernteaktuell, übrige Konzentrate nach DLG-Standard; **sidP/Mineralien** aus vollständigen DLG-Tabellen oder Analyse ergänzen (nicht aus RP schätzen). **Excel-/CSV-Vorlage** für LP-Ergänzungsfelder: `data/reference/dlg_2025_lp_import_template.xlsx` (Kopie; Aktualisierung: `python scripts/import_dlg_lp_template_from_xlsx.py`). **Befüllt + Quellen:** `data/reference/dlg_2025_lp_import_filled_sourced.xlsx` / `.csv` (`python scripts/import_dlg_lp_filled_from_xlsx.py`). **Merge** Referenz + befüllt → `dlg_merged_feeds_lp.csv`: `python scripts/merge_dlg_reference_to_lp_csv.py` (Loader: `app.utils.dlg_merged_csv`).

### Constraints Implemented
1. Dry matter intake equality
2. Minimum metabolizable energy
3. Minimum SIDP
4. Minimum and maximum aNDFom
5. Maximum starch
6. Maximum sugar
7. Maximum fat
8. Minimum calcium
9. Minimum phosphorus
10. Minimum sodium
11. Minimum forage share
12. Individual feed minimum/maximum usage limits

## Project Structure

```
rationsoptimierung/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   └── routes/             # API route handlers
│   │       ├── health.py       # Health check endpoint
│   │       ├── feeds.py        # Feed management endpoints
│   │       ├── requirements.py # Requirement calculation endpoints
│   │       └── optimization.py # Optimization endpoints
│   ├── schemas/                # Pydantic models for request/response validation
│   │   ├── feed.py             # FeedIngredient schema
│   │   ├── requirement.py      # NutrientRequirements schema
│   │   ├── optimization.py     # Optimization request/response schemas
│   │   └── common.py           # Shared response schemas
│   ├── domain/                 # Core business logic and models
│   │   ├── models.py           # CowProfile, AnimalGroup domain models
│   │   └── enums.py            # Domain enumerations
│   ├── nutrition/              # GfE-2023 Näherungsformeln (ME, ECM, sidP, Grenzen)
│   │   └── gfe2023.py
│   ├── services/               # Business logic services
│   │   ├── feed_service.py     # Feed ingredient management
│   │   └── requirement_service.py # Nutrient requirement calculation (nutzt gfe2023)
│   ├── optimization/           # Linear optimization implementation
│   │   ├── ration_model.py     # PuLP optimization model
│   │   └── solver.py           # Optimization service coordinator
│   └── utils/                  # Utility functions (to be expanded)
├── data/                       # Sample data files
│   ├── sample_feeds.csv        # Sample feed ingredients
│   └── sample_requirements.json # Sample nutrient requirements
├── tests/                      # Test suite
│   ├── test_health.py          # Health endpoint tests
│   ├── test_feeds.py           # Feed management tests
│   ├── test_requirements.py    # Requirement calculation tests
│   └── test_optimization.py    # Optimization endpoint tests
├── docs/                       # Documentation
│   └── valeo_integration.md    # ERP integration guidelines
├── Dockerfile                  # Docker container definition
├── docker-compose.yml          # Docker Compose configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- Docker (optional, for containerized deployment)

### Local Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd rationsoptimierung
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Access the API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Installation

1. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. The API will be available at http://localhost:8000

3. Access the API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /health` - Returns service health status

### Feed Management
- `GET /api/v1/feeds` - List all feed ingredients (optionally filter by group)
- `GET /api/v1/feeds/{feed_id}` - Get specific feed by ID
- `POST /api/v1/feeds/validate` - Validate feed ingredients
- `POST /api/v1/feeds` - Create new feed ingredient
- `PUT /api/v1/feeds/{feed_id}` - Update existing feed ingredient
- `DELETE /api/v1/feeds/{feed_id}` - Delete feed ingredient

### Requirement Calculation
- `POST /api/v1/requirements/calculate` - Calculate nutrient requirements from cow profile
- `POST /api/v1/requirements/maintenance` - Calculate maintenance requirements for dry cow

### Optimization
- `POST /api/v1/optimize` - Optimize ration for given cow profile, requirements, and feeds
- `POST /api/v1/optimize/demo` - Run demo optimization with sample data
- `POST /api/v1/optimize/from-profile` - JSON-Body `OptimizeFromProfileRequest`: `cow_profile` (Pflicht), optional `feeds` (Futtermittel-IDs; weglassen = alle aktiven), optional `options`. Ohne `target_dmi_kg` wird TM geschätzt (GfE-kompatibel mit typischer Energiekonzentration im LP).

## Usage Examples

### Calculate Requirements from Cow Profile

```bash
curl -X POST 'http://localhost:8000/api/v1/requirements/calculate' \
  -H 'Content-Type: application/json' \
  -d '{
    "breed": "Holstein",
    "body_weight_kg": 650,
    "milk_kg_day": 35,
    "milk_fat_pct": 3.8,
    "milk_protein_pct": 3.2,
    "lactation_stage_days": 150,
    "parity": 2,
    "target_dmi_kg": 22.0
  }'
```

### Run Demo Optimization

```bash
curl -X POST 'http://localhost:8000/api/v1/optimize/demo'
```

### Optimize Ration with Custom Data

```bash
curl -X POST 'http://localhost:8000/api/v1/optimize' \
  -H 'Content-Type: application/json' \
  -d '{
    "cow_profile": {
      "breed": "Holstein",
      "body_weight_kg": 650,
      "milk_kg_day": 35,
      "milk_fat_pct": 3.8,
      "milk_protein_pct": 3.2,
      "lactation_stage_days": 150,
      "parity": 2,
      "target_dmi_kg": 22.0
    },
    "requirements": {
      "dmi_kg": 22.0,
      "me_min_mj": 220.0,
      "sidp_min_g": 3200,
      "andfom_min_g": 5500,
      "andfom_max_g": 7500,
      "starch_max_g": 4000,
      "sugar_max_g": 1000,
      "fat_max_g": 1200,
      "ca_min_g": 100,
      "p_min_g": 60,
      "na_min_g": 8,
      "forage_share_min": 0.4
    },
    "feeds": [
      {
        "id": "grassilage",
        "name": "Grassilage",
        "group": "forage",
        "dm_frac": 0.35,
        "price_eur_kgdm": 0.15,
        "me_mj_kgdm": 10.5,
        "sidp_g_kgdm": 180,
        "andfom_g_kgdm": 450,
        "starch_g_kgdm": 20,
        "sugar_g_kgdm": 15,
        "fat_g_kgdm": 30,
        "ca_g_kgdm": 6,
        "p_g_kgdm": 3,
        "na_g_kgdm": 1,
        "min_kgdm": 0.0,
        "max_kgdm": 15.0,
        "active": true
      }
    ],
    "options": {
      "objective": "least_cost",
      "allow_infeasible_soft_constraints": false,
      "export_dual_values": false,
      "export_slacks": false,
      "max_solver_time_sec": 30,
      "solver_name": "CBC"
    }
  }'
```

## Sample Data

The project includes sample data files in the `data/` directory:

- `sample_feeds.csv`: Contains 18 sample feed ingredients with typical nutritional values and prices
- `sample_requirements.json`: Contains sample nutrient requirements for a high-producing Holstein cow

**Note**: These values are for demonstration purposes only. Real laboratory analyses and current purchase prices must be used for production ration optimization.

## Testing

Run the test suite with pytest:

```bash
pytest tests/
```

Or run individual test files:

```bash
pytest tests/test_health.py
pytest tests/test_feeds.py
pytest tests/test_requirements.py
pytest tests/test_optimization.py
```

## ERP Integration

This tool is designed for later integration with the VALEO ERP Agrarportal. See `docs/valeo_integration.md` for detailed integration guidelines including:

- API versioning strategy
- Authentication options
- Data mapping recommendations
- Potential ERP workflows
- Repository interfaces for future implementation

## Development Guidelines

### Code Quality
- Type hints for all function parameters and return values
- Comprehensive docstrings following Google/NumPy style
- Structured logging with appropriate log levels
- Meaningful error messages and validation
- Modular, testable code design

### Extensibility
- New feed attributes can be added to `FeedIngredient` schema
- New constraints can be added to the optimization model
- New objectives can be implemented by modifying the objective function
- Service interfaces are designed for easy replacement with database implementations

### Future Enhancements
- Integration with actual laboratory analysis systems
- Real-time price updates from ERP systems
- Advanced optimization objectives (e.g., minimize environmental impact)
- Sensitivity analysis and shadow price reporting
- Batch optimization for multiple animal groups
- User interface for manual ration adjustment

## Limitations and Disclaimers

### MVP Status
This is a Minimum Viable Product (MVP) implementation intended for demonstration and further development. It includes:

- Placeholder values in sample data that must be replaced with real laboratory analyses and current prices
- Simplified requirement calculation heuristics (to be replaced with GfE-2023 formulas)
- Basic constraint set (expandable for additional nutrients and factors)

### Not Official Feeding Advice
**IMPORTANT**: This tool provides optimization suggestions based on mathematical models. It does not replace professional nutritional advice from qualified animal nutritionists or veterinarians. Always consult with a professional before making significant changes to animal feeding programs.

### Data Quality Dependence
The quality of optimization results is directly dependent on the quality of input data:
- Accurate feed nutritional analyses
- Current and accurate feed prices
- Correct animal performance data
- Appropriate constraint values

## License

This project is proprietary software developed for VALEO ERP. All rights reserved.

## Contact

For questions or support regarding this tool, please contact the VALEO ERP development team.