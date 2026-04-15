from fastapi import APIRouter, HTTPException

from makemkv_headless_api.api.api_response import APIResponse
from makemkv_headless_api.api.state import STATE

router = APIRouter(prefix="/error")

@router.get('')
@router.get('/')
def get_error_state():
  return APIResponse(status="success", data=STATE.error)

@router.get(".clear")
def clear_error_state():
  STATE.error = None
  return APIResponse(status="success")

@router.get(".test")
def test_error_state():
  STATE.error = None
  raise Exception("There was an error")