import sys, os, traceback

sys.path.insert(0, os.path.abspath('backend'))

try:
    m = __import__('api.ai_workflow_api', fromlist=['router'])
    print('IMPORT_OK', getattr(m, 'router', None).prefix)
except Exception as e:
    print('IMPORT_FAIL', repr(e))
    traceback.print_exc()

