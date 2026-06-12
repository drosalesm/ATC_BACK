from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.db.database import get_db
from app.models.users import User  # Make sure the User model is imported
from app.utils.auth import decode_access_token, create_access_token  # Add utils for token
from app.utils.auth import verify_password  # Utility to verify passwords



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Authentication logic for extracting user from token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Decode and validate the token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Invalido")
    
    # Query the user from the database
    user = db.query(User).filter(User.username == payload.get("sub")).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="El usuario con el que se genero el token no existe")
    
    return user
