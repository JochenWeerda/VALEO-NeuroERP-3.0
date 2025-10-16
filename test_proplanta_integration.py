#!/usr/bin/env python3
"""
Test script for Proplanta PSM Integration
Tests the MCP server and ERP integration
"""

import requests
import json
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
ERP_BASE_URL = "http://localhost:8000"  # Adjust as needed
MCP_CONFIG_PATH = Path("c:/Users/Jochen/AppData/Roaming/Kilo-Code/MCP/proplanta-psm-scraper/package.json")
DEV_TOKEN = "dev-token"  # Development token for testing
HEADERS = {"Authorization": f"Bearer {DEV_TOKEN}"}

def test_mcp_server():
    """Test MCP server configuration and basic functionality"""
    logger.info("Testing MCP server configuration...")

    # Check if MCP server directory exists
    mcp_dir = Path("c:/Users/Jochen/AppData/Roaming/Kilo-Code/MCP/proplanta-psm-scraper")
    if not mcp_dir.exists():
        logger.error(f"MCP server directory not found at {mcp_dir}")
        return False

    # Check if package.json exists
    if not MCP_CONFIG_PATH.exists():
        logger.error(f"MCP package.json not found at {MCP_CONFIG_PATH}")
        return False

    try:
        with open(MCP_CONFIG_PATH, 'r') as f:
            package_data = json.load(f)

        # Check if it's a valid Node.js package
        if not package_data.get('name') == 'proplanta-psm-scraper':
            logger.error("Invalid MCP server package")
            return False

        logger.info("✓ MCP server configuration found")
        return True

    except Exception as e:
        logger.error(f"Failed to read MCP config: {e}")
        return False

def test_erp_endpoints():
    """Test ERP API endpoints for PSM integration"""
    logger.info("Testing ERP API endpoints...")

    endpoints_to_test = [
        "/api/v1/agrar/psm/proplanta/status",
        "/api/v1/agrar/psm/proplanta/list",
        "/api/v1/agrar/psm/proplanta/stats/overview"
    ]

    for endpoint in endpoints_to_test:
        try:
            url = f"{ERP_BASE_URL}{endpoint}"
            logger.info(f"Testing endpoint: {url}")

            response = requests.get(url, headers=HEADERS, timeout=10)

            if response.status_code == 200:
                logger.info(f"✓ Endpoint {endpoint} accessible")
                try:
                    data = response.json()
                    logger.info(f"  Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    logger.info(f"  Response: {response.text[:200]}...")
            else:
                logger.warning(f"⚠ Endpoint {endpoint} returned status {response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Failed to access {endpoint}: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Unexpected error testing {endpoint}: {e}")
            return False

    return True

def test_psm_sync():
    """Test PSM data synchronization"""
    logger.info("Testing PSM data synchronization...")

    try:
        url = f"{ERP_BASE_URL}/api/v1/agrar/psm/proplanta/sync"
        logger.info(f"Triggering PSM sync: {url}")

        response = requests.post(url, headers=HEADERS, timeout=30)

        if response.status_code == 200:
            data = response.json()
            logger.info(f"✓ PSM sync initiated: {data}")
            return True
        else:
            logger.error(f"✗ PSM sync failed with status {response.status_code}: {response.text}")
            return False

    except Exception as e:
        logger.error(f"✗ PSM sync test failed: {e}")
        return False

def test_psm_search():
    """Test PSM search functionality"""
    logger.info("Testing PSM search functionality...")

    try:
        # Test search endpoint
        url = f"{ERP_BASE_URL}/api/v1/agrar/psm/proplanta/search"
        params = {"q": "glyphosate", "limit": 5}

        logger.info(f"Testing PSM search: {url} with params {params}")

        response = requests.get(url, headers=HEADERS, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            logger.info(f"✓ PSM search successful, found {len(data)} results")
            return True
        else:
            logger.warning(f"⚠ PSM search returned status {response.status_code}: {response.text}")
            return False

    except Exception as e:
        logger.error(f"✗ PSM search test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    logger.info("Starting Proplanta PSM Integration Tests")
    logger.info("=" * 50)

    tests = [
        ("MCP Server Configuration", test_mcp_server),
        ("ERP API Endpoints", test_erp_endpoints),
        ("PSM Synchronization", test_psm_sync),
        ("PSM Search", test_psm_search)
    ]

    results = []

    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✓ {test_name} PASSED")
            else:
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} FAILED with exception: {e}")
            results.append((test_name, False))

        # Small delay between tests
        time.sleep(1)

    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST SUMMARY")

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1

    logger.info(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed! Proplanta PSM integration is working correctly.")
        return 0
    else:
        logger.error(f"❌ {total - passed} test(s) failed. Please check the integration setup.")
        return 1

if __name__ == "__main__":
    exit(main())