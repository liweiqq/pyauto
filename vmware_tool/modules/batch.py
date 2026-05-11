from __future__ import annotations

from pathlib import Path

class BatchOperator:
    def __init__(self, clone_mgr, pass_mgr, modify_mgr) -> None:
        self.clone_mgr = clone_mgr
        self.pass_mgr = pass_mgr
        self.modify_mgr = modify_mgr

    def run_batch(self, file_path: str) -> dict:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(file_path)
        import pandas as pd
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)

        results = []
        for _, row in df.iterrows():
            action = row.get("action")
            if action == "clone":
                results.append({"row": int(_), "status": "queued", "action": "clone"})
            elif action == "password":
                results.append({"row": int(_), "status": "queued", "action": "password"})
            elif action == "modify":
                results.append({"row": int(_), "status": "queued", "action": "modify"})
            else:
                results.append({"row": int(_), "status": "ignored", "action": action})
        return {"total": len(results), "results": results}
