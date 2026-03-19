"""
Test for requirements calculation
"""
from app.domain.models import CowProfile, Breed


def test_calculate_requirements(client):
    """Test calculating nutrient requirements from cow profile"""
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
    
    response = client.post("/api/v1/requirements/calculate", json=cow_profile)
    assert response.status_code == 200
    data = response.json()
    
    # Check that we got the expected fields
    assert "dmi_kg" in data
    assert "me_min_mj" in data
    assert "sidp_min_g" in data
    assert "andfom_min_g" in data
    assert "andfom_max_g" in data
    assert "starch_max_g" in data
    assert "sugar_max_g" in data
    assert "fat_max_g" in data
    assert "ca_min_g" in data
    assert "p_min_g" in data
    assert "na_min_g" in data
    assert "forage_share_min" in data
    
    # Check that values are reasonable
    assert data["dmi_kg"] > 0
    assert data["me_min_mj"] > 0
    assert data["sidp_min_g"] > 0
    assert data["andfom_min_g"] > 0
    assert data["andfom_max_g"] >= data["andfom_min_g"]
    assert data["starch_max_g"] >= 0
    assert data["sugar_max_g"] >= 0
    assert data["fat_max_g"] >= 0
    assert data["ca_min_g"] > 0
    assert data["p_min_g"] > 0
    assert data["na_min_g"] > 0
    assert 0 <= data["forage_share_min"] <= 1

def test_calculate_maintenance_requirements(client):
    """Test calculating maintenance requirements"""
    body_weight_kg = 650
    
    response = client.post(f"/api/v1/requirements/maintenance?body_weight_kg={body_weight_kg}")
    assert response.status_code == 200
    data = response.json()
    
    # Check that we got the expected fields
    assert "dmi_kg" in data
    assert "me_min_mj" in data
    assert "sidp_min_g" in data
    assert "andfom_min_g" in data
    assert "andfom_max_g" in data
    assert "starch_max_g" in data
    assert "sugar_max_g" in data
    assert "fat_max_g" in data
    assert "ca_min_g" in data
    assert "p_min_g" in data
    assert "na_min_g" in data
    assert "forage_share_min" in data
    
    # For a dry cow, we expect higher forage share
    assert data["forage_share_min"] >= 0.5
    
    # Check that values are reasonable
    assert data["dmi_kg"] > 0
    assert data["me_min_mj"] > 0
    assert data["sidp_min_g"] > 0
    assert data["andfom_min_g"] > 0
    assert data["andfom_max_g"] >= data["andfom_min_g"]
    assert data["starch_max_g"] >= 0
    assert data["sugar_max_g"] >= 0
    assert data["fat_max_g"] >= 0
    assert data["ca_min_g"] > 0
    assert data["p_min_g"] > 0
    assert data["na_min_g"] > 0
    assert 0 <= data["forage_share_min"] <= 1

def test_calculate_maintenance_invalid_weight(client):
    """Test calculating maintenance requirements with invalid weight"""
    response = client.post("/api/v1/requirements/maintenance?body_weight_kg=0")
    assert response.status_code == 400  # Bad request
    
    response = client.post("/api/v1/requirements/maintenance?body_weight_kg=-100")
    assert response.status_code == 400  # Bad request