import copy
import json
import uuid
from typing import Any, Dict, List, Optional


class MockResponse:
    def __init__(self, data: List[Dict[str, Any]], count: Optional[int] = None):
        self.data = data
        self.count = count if count is not None else len(data)


class MockQueryBuilder:
    def __init__(self, table_name: str, db: "MockSupabaseDB", user_id: str):
        self.table_name = table_name
        self.db = db
        self.user_id = user_id
        self._action = "select"
        self._filters: List[tuple] = []
        self._order_by: Optional[str] = None
        self._desc = False
        self._range_start = 0
        self._range_end: Optional[int] = None
        self._insert_data: Optional[Dict[str, Any]] = None
        self._update_data: Optional[Dict[str, Any]] = None
        self._count_mode: Optional[str] = None

    def select(self, columns: str = "*", count: Optional[str] = None):
        self._action = "select"
        self._count_mode = count
        return self

    def insert(self, data: Dict[str, Any]):
        self._action = "insert"
        self._insert_data = copy.deepcopy(data)
        return self

    def update(self, data: Dict[str, Any]):
        self._action = "update"
        self._update_data = copy.deepcopy(data)
        return self

    def delete(self):
        self._action = "delete"
        return self

    def eq(self, column: str, value: Any):
        self._filters.append(("eq", column, str(value)))
        return self

    def ilike(self, column: str, pattern: str):
        self._filters.append(("ilike", column, pattern))
        return self

    def order(self, column: str, desc: bool = False):
        self._order_by = column
        self._desc = desc
        return self

    def range(self, start: int, end: int):
        self._range_start = start
        self._range_end = end
        return self

    def execute(self) -> MockResponse:
        if self._action == "insert":
            return self._execute_insert()
        elif self._action == "update":
            return self._execute_update()
        elif self._action == "delete":
            return self._execute_delete()
        else:
            return self._execute_select()

    def _execute_insert(self) -> MockResponse:
        row = copy.deepcopy(self._insert_data)
        if "id" not in row:
            row["id"] = str(uuid.uuid4())

        # Simulate PostgreSQL JSONB serialization round-trip
        if "test_ir" in row:
            row["test_ir"] = json.loads(json.dumps(row["test_ir"]))

        if self.table_name == "projects":
            # RLS: check owner_id == auth.uid()
            if row.get("owner_id") != self.user_id:
                raise Exception("new row violates row-level security policy for table \"projects\"")
            self.db.projects[row["id"]] = copy.deepcopy(row)
            return MockResponse([copy.deepcopy(row)])

        elif self.table_name == "tests":
            # RLS: check parent project owner_id == auth.uid()
            parent_id = row.get("project_id")
            parent = self.db.projects.get(parent_id)
            if not parent or parent.get("owner_id") != self.user_id:
                raise Exception("new row violates row-level security policy for table \"tests\"")
            self.db.tests[row["id"]] = copy.deepcopy(row)
            return MockResponse([copy.deepcopy(row)])

        raise NotImplementedError(f"Insert not supported for {self.table_name}")

    def _execute_select(self) -> MockResponse:
        results = []
        if self.table_name == "projects":
            # RLS: only return projects where owner_id == self.user_id
            for p in self.db.projects.values():
                if p.get("owner_id") == self.user_id:
                    results.append(copy.deepcopy(p))

        elif self.table_name == "tests":
            # RLS: only return tests whose parent project owner_id == self.user_id
            for t in self.db.tests.values():
                parent = self.db.projects.get(t.get("project_id"))
                if parent and parent.get("owner_id") == self.user_id:
                    results.append(copy.deepcopy(t))

        # Apply filters
        filtered = []
        for row in results:
            match = True
            for op, col, val in self._filters:
                if op == "eq":
                    if str(row.get(col)) != str(val):
                        match = False
                        break
                elif op == "ilike":
                    needle = val.strip("%").lower()
                    if needle not in str(row.get(col, "")).lower():
                        match = False
                        break
            if match:
                filtered.append(row)

        # Sort
        if self._order_by:
            filtered.sort(key=lambda x: str(x.get(self._order_by, "")), reverse=self._desc)

        total_count = len(filtered)
        if self._range_end is not None:
            paged = filtered[self._range_start : self._range_end + 1]
        else:
            paged = filtered[self._range_start :]

        return MockResponse(paged, count=total_count if self._count_mode == "exact" else None)

    def _execute_update(self) -> MockResponse:
        updated_rows = []
        update_payload = copy.deepcopy(self._update_data)
        if "test_ir" in update_payload:
            update_payload["test_ir"] = json.loads(json.dumps(update_payload["test_ir"]))

        # Find matching rows subject to RLS
        select_resp = self._execute_select()
        for row in select_resp.data:
            target_dict = self.db.projects if self.table_name == "projects" else self.db.tests
            target = target_dict[row["id"]]
            target.update(copy.deepcopy(update_payload))
            updated_rows.append(copy.deepcopy(target))
        return MockResponse(updated_rows)

    def _execute_delete(self) -> MockResponse:
        deleted_rows = []
        select_resp = self._execute_select()
        for row in select_resp.data:
            target_dict = self.db.projects if self.table_name == "projects" else self.db.tests
            deleted = target_dict.pop(row["id"], None)
            if deleted:
                deleted_rows.append(copy.deepcopy(deleted))
                # Cascading delete: if project deleted, delete associated tests
                if self.table_name == "projects":
                    tests_to_del = [
                        tid for tid, t in self.db.tests.items() if t.get("project_id") == row["id"]
                    ]
                    for tid in tests_to_del:
                        self.db.tests.pop(tid, None)
        return MockResponse(deleted_rows)


class MockSupabaseClient:
    def __init__(self, db: "MockSupabaseDB", user_id: str):
        self.db = db
        self.user_id = user_id

    def table(self, table_name: str) -> MockQueryBuilder:
        return MockQueryBuilder(table_name, self.db, self.user_id)


class MockSupabaseDB:
    def __init__(self):
        self.projects: Dict[str, Dict[str, Any]] = {}
        self.tests: Dict[str, Dict[str, Any]] = {}

    def get_client(self, user_id: str) -> MockSupabaseClient:
        return MockSupabaseClient(self, str(user_id))
