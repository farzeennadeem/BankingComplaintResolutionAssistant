"""Complaint routes (Exercise 3.2.2). Each route only calls the service;
the service decides what is allowed."""
from typing import Literal, Optional

from fastapi import APIRouter, Header, Request

from src.api.schemas import (Complaint, CreateComplaintRequest, CreateComplaintResult,
                             StatusUpdateRequest, StatusUpdateResult)

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.get("/{complaint_id}", response_model=Complaint)
def get_complaint(complaint_id: str, request: Request):
    return request.app.state.service.get_complaint(complaint_id)


@router.post("", response_model=CreateComplaintResult, status_code=201)
def create_complaint(body: CreateComplaintRequest, request: Request,
                     x_actor_id: Optional[str] = Header(default=None)):
    return request.app.state.service.create_complaint(
        body.customer_id, body.account_id, body.channel, body.category,
        body.complaint_text, body.priority, actor_id=x_actor_id)


@router.patch("/{complaint_id}/status", response_model=StatusUpdateResult)
def change_status(complaint_id: str, body: StatusUpdateRequest, request: Request,
                  x_actor_role: Literal["Analyst", "Supervisor"] = Header(),
                  x_actor_id: Optional[str] = Header(default=None)):
    return request.app.state.service.change_status(
        complaint_id, body.target_status, body.reason, role=x_actor_role, actor_id=x_actor_id)
