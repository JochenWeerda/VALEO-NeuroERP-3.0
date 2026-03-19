"""
Test for feed validation
"""
from app.schemas.feed import FeedIngredient, FeedGroup


def test_get_feeds(client):
    """Test getting all feeds"""
    response = client.get("/api/v1/feeds")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check that we have the expected fields
    assert "id" in data[0]
    assert "name" in data[0]
    assert "group" in data[0]

def test_get_feeds_by_group(client):
    """Test getting feeds by group"""
    response = client.get("/api/v1/feeds?group=forage")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # All returned feeds should be forage
    for feed in data:
        assert feed["group"] == "forage"

def test_get_specific_feed(client):
    """Test getting a specific feed by ID"""
    response = client.get("/api/v1/feeds/grassilage")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "grassilage"
    assert data["name"] == "Grassilage"

def test_get_nonexistent_feed(client):
    """Test getting a nonexistent feed"""
    response = client.get("/api/v1/feeds/nonexistent")
    assert response.status_code == 404

def test_validate_feeds(client):
    """Test feed validation endpoint"""
    # Valid feed
    valid_feed = {
        "id": "test_feed",
        "name": "Test Feed",
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
        "active": True
    }
    
    response = client.post("/api/v1/feeds/validate", json=[valid_feed])
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    
    # Invalid: duplicate feed IDs (passes Pydantic but fails business validation)
    duplicate_feed = valid_feed.copy()
    duplicate_feed["id"] = valid_feed["id"]
    duplicate_feed["name"] = "Different Name Same ID"
    duplicate_feeds = [valid_feed, duplicate_feed]
    
    response = client.post("/api/v1/feeds/validate", json=duplicate_feeds)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False

def test_create_feed(client):
    """Test creating a new feed"""
    new_feed = {
        "id": "new_test_feed",
        "name": "New Test Feed",
        "group": "concentrate",
        "dm_frac": 0.88,
        "price_eur_kgdm": 0.20,
        "me_mj_kgdm": 12.0,
        "sidp_g_kgdm": 100,
        "andfom_g_kgdm": 50,
        "starch_g_kgdm": 400,
        "sugar_g_kgdm": 50,
        "fat_g_kgdm": 20,
        "ca_g_kgdm": 1,
        "p_g_kgdm": 3,
        "na_g_kgdm": 0.5,
        "min_kgdm": 0.0,
        "max_kgdm": 5.0,
        "active": True
    }
    
    response = client.post("/api/v1/feeds", json=new_feed)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "new_test_feed"
    assert data["name"] == "New Test Feed"
    
    # Clean up - delete the feed we just created
    response = client.delete("/api/v1/feeds/new_test_feed")
    assert response.status_code == 200

def test_create_duplicate_feed(client):
    """Test creating a feed with duplicate ID"""
    # Try to create a feed with an ID that already exists
    existing_feed = {
        "id": "grassilage",  # This already exists
        "name": "Duplicate Grassilage",
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
        "active": True
    }
    
    response = client.post("/api/v1/feeds", json=existing_feed)
    assert response.status_code == 400  # Bad request