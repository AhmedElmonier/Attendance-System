from uuid import UUID
from typing import Dict, Any, Optional
from src.models.governance import ApprovalRequest


def apply_changes(
    entity_type: str, entity_id: UUID, change_payload: Dict[str, Any]
) -> bool:
    # TODO(#issue): implement entity mutation for approval workflow
    # - EMPLOYEE: update name_ar, name_en, status
    # - BIOMETRIC: replace biometric_templates vector_blob
    # - SITE: update site configuration
    # - Must be idempotent and record old_values in AuditLog
    raise NotImplementedError(
        f"apply_changes not implemented for entity type '{entity_type}'. "
        "Implement before approving requests."
    )


class ApprovalService:
    def __init__(self, db_session):
        self.db = db_session

    def create_request(
        self,
        tenant_id: UUID,
        maker_id: UUID,
        entity_type: str,
        entity_id: UUID,
        payload: Dict[str, Any],
    ) -> ApprovalRequest:
        request = ApprovalRequest(
            tenant_id=tenant_id,
            maker_id=maker_id,
            entity_type=entity_type,
            entity_id=entity_id,
            change_payload=payload,
            status="PENDING",
        )
        self.db.add(request)
        try:
            self.db.commit()
            self.db.refresh(request)
        except Exception:
            self.db.rollback()
            raise
        return request

    def review_request(
        self,
        request_id: UUID,
        tenant_id: UUID,
        checker_id: UUID,
        action: str,
        reason: Optional[str] = None,
    ) -> ApprovalRequest:
        request = (
            self.db.query(ApprovalRequest)
            .filter(
                ApprovalRequest.id == request_id,
                ApprovalRequest.tenant_id == tenant_id,
            )
            .first()
        )
        if not request:
            raise ValueError("Approval request not found")

        if str(request.maker_id) == str(checker_id):
            raise ValueError(
                "Self-approval is forbidden. A different user must approve this request."
            )

        if request.status != "PENDING":
            raise ValueError(
                f"Cannot review request. Currently in state: {request.status}"
            )

        if action not in ["APPROVED", "REJECTED"]:
            raise ValueError("Invalid action. Must be APPROVED or REJECTED")

        request.checker_id = checker_id
        request.reason = reason

        if action == "APPROVED":
            try:
                apply_changes(
                    request.entity_type, request.entity_id, request.change_payload
                )
            except NotImplementedError as e:
                self.db.rollback()
                raise ValueError(str(e)) from e

        request.status = action

        try:
            self.db.commit()
            self.db.refresh(request)
        except Exception:
            self.db.rollback()
            raise

        return request
