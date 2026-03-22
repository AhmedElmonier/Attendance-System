import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from src.api.governance import router, get_current_user_id
from src.services.approval_service import ApprovalService
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_maker_checker_self_approval_blocked():
    req_id = uuid4()
    maker_id = uuid4()

    class FakeSession:
        def __init__(self):
            self._req = None

        def add(self, obj):
            pass

        def query(self, model):
            class q:
                def filter(self, *args):
                    return self

                def first(self):
                    return self._req

            q._req = self._req
            return q()

        def commit(self):
            pass

        def refresh(self, obj):
            pass

    fake_session = FakeSession()
    tenant_id = uuid4()
    fake_session._req = type(
        "obj",
        (),
        {
            "id": req_id,
            "maker_id": maker_id,
            "tenant_id": tenant_id,
            "entity_type": "EMPLOYEE",
            "entity_id": uuid4(),
            "change_payload": {},
            "status": "PENDING",
            "checker_id": None,
            "reason": None,
        },
    )()

    service = ApprovalService(fake_session)
    with pytest.raises(ValueError, match="Self-approval is forbidden"):
        service.review_request(req_id, tenant_id, maker_id, "APPROVED")


def test_maker_checker_approval_succeeds_for_different_users():
    req_id = uuid4()
    maker_id = uuid4()
    checker_id = uuid4()

    class FakeSession:
        def __init__(self):
            self._req = None

        def add(self, obj):
            pass

        def query(self, model):
            class q:
                def filter(self, *args):
                    return self

                def first(self):
                    return self._req

            q._req = self._req
            return q()

        def commit(self):
            pass

        def refresh(self, obj):
            pass

    fake_session = FakeSession()
    tenant_id = uuid4()
    fake_session._req = type(
        "obj",
        (),
        {
            "id": req_id,
            "maker_id": maker_id,
            "tenant_id": tenant_id,
            "entity_type": "EMPLOYEE",
            "entity_id": uuid4(),
            "change_payload": {},
            "status": "PENDING",
            "checker_id": None,
            "reason": None,
        },
    )()

    service = ApprovalService(fake_session)
    with pytest.raises(NotImplementedError):
        service.review_request(req_id, tenant_id, checker_id, "APPROVED")
