def test_endpoints_package_imports():
    import app.api.v1.endpoints as endpoints

    assert endpoints is not None


def test_main_module_imports():
    import main

    assert main.app is not None
