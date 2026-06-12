from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError
from app.routers import auth, categories,products,company #,customer,taxes,waitlist,unemploymentClaims,analitics
from fastapi.responses import JSONResponse
#from app.middleware.logging_middleware import log_request_response
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine


# Imports de modelos — necesarios para que create_all los detecte
from app.models.products import Product, Category
from app.models.users import User
from app.models.company import Company
Base.metadata.create_all(bind=engine)



app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(company.router, prefix="/company", tags=["Company"])
    

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


# Global error handler for database connection issues
@app.exception_handler(OperationalError)
async def db_exception_handler(request, exc):
    return JSONResponse(
        status_code=503,
        content={"message": "Database unavailable", "status": "error", "http_code": 503, "data": []},
    )
