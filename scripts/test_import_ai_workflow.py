import traceback

try:
    import backend.api.ai_workflow_api as m
    print("IMPORT_OK", m.router.prefix)
except Exception as e:
    print("IMPORT_FAIL", repr(e))
    traceback.print_exc()

