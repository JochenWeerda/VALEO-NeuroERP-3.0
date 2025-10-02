import os
os.environ.setdefault("USE_CHROMA", "0")

from backend.main import app
from fastapi.testclient import TestClient

def main() -> None:
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/api/ai-workflow/query", params={"q": "LangGraph Workflow", "n": 2})
        print("STATUS:", resp.status_code)
        print("BODY:")
        try:
            print(resp.text)
        except Exception as e:
            print("<decode error>", e)

if __name__ == "__main__":
    main()


