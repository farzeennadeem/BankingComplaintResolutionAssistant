"""Customer routes (Exercise 3.2.2). Each route only calls the service."""
from fastapi import APIRouter, Request

from src.api.schemas import Customer, CustomerComplaints

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/{customer_id}", response_model=Customer)
def get_customer(customer_id: str, request: Request):
    return request.app.state.service.get_customer(customer_id)


@router.get("/{customer_id}/complaints", response_model=CustomerComplaints)
def get_customer_complaints(customer_id: str, request: Request):
    return request.app.state.service.get_customer_complaints(customer_id)
