from uuid import UUID
from typing import Dict, Any, Optional
from src.models.governance import ApprovalRequest
# Assuming Session is injected/passed
class ApprovalService:
    def __init__(self, db_session):
        self.db = db_session

    def create_request(self, tenant_id: UUID, maker_id: UUID, entity_type: str, entity_id: UUID, payload: Dict[str, Any]) -> ApprovalRequest:
        request = ApprovalRequest(
            tenant_id=tenant_id,
            maker_id=maker_id,
            entity_type=entity_type,
            entity_id=entity_id,
            change_payload=payload,
            status='PENDING'
        )
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request

    def review_request(self, request_id: UUID, checker_id: UUID, action: str, reason: str = None) -> ApprovalRequest:
        request = self.db.query(ApprovalRequest).filter(ApprovalRequest.id == request_id).first()
        if not request:
            raise ValueError("Approval request not found")
        
        if str(request.maker_id) == str(checker_id):
            raise ValueError("Self-approval is forbidden. A different user must approve this request.")

        if request.status != 'PENDING':
            raise ValueError(f"Cannot review request. Currently in state: {request.status}")
        
        if action not in ['APPROVED', 'REJECTED']:
            raise ValueError("Invalid action. Must be APPROVED or REJECTED")

        request.status = action
        request.checker_id = checker_id
        request.reason = reason
        
        # In a real app, if APPROVED, we would apply the change_payload to the target entity here.
        # e.g., apply_changes(request.entity_type, request.entity_id, request.change_payload)

        self.db.commit()
        self.db.refresh(request)
        return request
