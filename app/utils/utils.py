from fastapi.responses import JSONResponse
import uuid
#from app.models.customer import Customer
#from app.models.taxes import Taxes
from sqlalchemy.orm import class_mapper
from typing import List
import re
from datetime import datetime, date, timedelta

def is_valid_email(email):
    email_regex = r'^[^@]+@[^@]+\.[^@]+$'
    return re.match(email_regex, email)


def format_response(http_code: int, message: str, data=None,request=None):
    """Formats API responses dynamically based on HTTP status codes."""
    status_map = {
        201: "Ok",
        200: "Ok",        
        400: "bad_request",
        404: "No hay informacion",
        500: "error",
    }

    status = status_map.get(http_code, "error")  # Default to 'error' if unknown code
    uti = str(uuid.uuid4())

    return JSONResponse(
        status_code=http_code,
        content={
            "uti": uti,                        
            "message": message,
            "status": status,
            "http_code": http_code,
            "data": data or []        },
    )
