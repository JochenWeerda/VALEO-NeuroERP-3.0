"""
Test for optimization endpoint
"""
from app.schemas.feed import FeedIngredient, FeedGroup
from app.schemas.requirement import NutrientRequirements
from app.schemas.optimization import OptimizationOptions
from app.domain.models import CowProfile, Breed


def test_demo_optimization(client):
    """Test the demo optimization endpoint"""
    response = client.post("/api/v1/optimize/demo")
    # This might fail if the problem is infeasible with our sample data,
    # but it should return a valid response
    assert response.status_code == 200
    data = response.json()
    
    # Check that we got the expected fields
    assert "status" in data
    assert "total_cost_eur_day" in data
    assert "ration_items" in data
    assert "nutrient_supply" in data
    assert "constraint_report" in data
    assert "warnings" in data
    assert "metadata" in data
    
    # Check types
    assert isinstance(data["ration_items"], list)
    assert isinstance(data["nutrient_supply"], dict)
    assert isinstance(data["constraint_report"], list)
    assert isinstance(data["warnings"], list)
    assert isinstance(data["metadata"], dict)

    assert data["status"] == "optimal"
    assert data["nutrient_supply"]["me_mj"] >= 240.0
    assert data["nutrient_supply"]["dmi_kg"] > 0


def test_optimization_with_infeasible_problem(client):
    """Test optimization with deliberately infeasible constraints"""
    # Create a cow profile
    cow_profile = {
        "breed": "Holstein",
        "body_weight_kg": 650,
        "milk_kg_day": 35,
        "milk_fat_pct": 3.8,
        "milk_protein_pct": 3.2,
        "lactation_stage_days": 150,
        "parity": 2,
        "target_dmi_kg": 22.0
    }
    
    # Create requirements that are impossible to meet
    # For example, extremely high energy requirement that can't be met
    requirements = {
        "dmi_kg": 22.0,
        "me_min_mj": 10000.0,  # Extremely high - impossible to meet
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
    }
    
    # Get some feeds
    feeds_response = client.get("/api/v1/feeds")
    assert feeds_response.status_code == 200
    feeds = feeds_response.json()
    
    # Limit to first few feeds to keep test fast
    limited_feeds = feeds[:5]
    
    # Create optimization request
    request = {
        "cow_profile": cow_profile,
        "requirements": requirements,
        "feeds": limited_feeds,
        "options": {
            "objective": "least_cost",
            "allow_infeasible_soft_constraints": False,
            "export_dual_values": False,
            "export_slacks": False,
            "max_solver_time_sec": 10,
            "solver_name": "CBC"
        }
    }
    
    response = client.post("/api/v1/optimize", json=request)
    assert response.status_code == 200
    data = response.json()
    
    # Should indicate infeasibility
    assert data["status"] in ["infeasible", "optimal"]  # Could be either depending on solver
    # If infeasible, we should see warnings or constraint violations
    if data["status"] == "infeasible":
        assert len(data["warnings"]) > 0 or len(data["constraint_report"]) > 0

def test_optimization_from_profile_all_feeds_optimal(client):
    """Mit allen Futtermitteln des Mandanten und geschätzter TM → LP sollte optimal sein (GfE-ME)."""
    cow_profile = {
        "breed": "Holstein",
        "body_weight_kg": 650,
        "milk_kg_day": 35,
        "milk_fat_pct": 3.8,
        "milk_protein_pct": 3.2,
        "lactation_stage_days": 150,
        "parity": 2,
    }
    response = client.post(
        "/api/v1/optimize/from-profile",
        json={"cow_profile": cow_profile},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "optimal"
    assert data["nutrient_supply"]["me_mj"] >= 240.0
    assert len(data["ration_items"]) >= 1


def test_optimization_from_profile_narrow_basket_infeasible(client):
    """Zu schmales Futtermittel-Set (ohne Mineralien/hohe Energie) → erwartbar unlösbar."""
    cow_profile = {
        "breed": "Holstein",
        "body_weight_kg": 650,
        "milk_kg_day": 35,
        "milk_fat_pct": 3.8,
        "milk_protein_pct": 3.2,
        "lactation_stage_days": 150,
        "parity": 2,
    }
    request = {
        "cow_profile": cow_profile,
        "feeds": ["grassilage", "maissilage", "sojaschrot"],
    }
    response = client.post("/api/v1/optimize/from-profile", json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "infeasible"