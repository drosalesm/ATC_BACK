from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.db.database import get_db
from app.models.users import User
from app.utils.auth import verify_password, get_password_hash, create_access_token,decode_access_token
from fastapi import Form
from app.schemas.auth import UserCreate,UserUpdate
from app.auth.auth import get_current_user
from app.utils.utils import format_response

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    print('Entrando al modulo de autenticacion...')

    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    
    if existing_user:
        return format_response(400, "El nombre de usuario ya está en uso")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_password, 
        role=user.role, 
        name=user.name,
        status=user.status
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Data del usuario creado
    user_data = {
        "id": new_user.id, 
        "username": new_user.username, 
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role
    }
    
    return format_response(201, "Usuario creado exitosamente", user_data)


@router.post("/token")
def login_for_access_token(data: dict, db: Session = Depends(get_db)):
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return format_response(400, "Username and password required")

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return format_response(401, "Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})
    
    token_data = {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    }
    
    return format_response(200, "Login successful", token_data)



@router.get("/users")
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        users = db.query(User).all()

        if not users:
            return format_response(404, "No users found")

        # Serialize users
        users_list = [
            {
                "id": user.id, 
                "username": user.username, 
                "email": user.email,
                "role": user.role,
                "name": user.name,
                "status": user.status
            } 
            for user in users
        ]

        return format_response(200, "Users retrieved successfully", users_list)
    
    except Exception as e:
        print(e)
        return format_response(500, "Internal Server Error")


@router.put("/users/{user_id}")
def update_user(
    user_id: int, 
    user_data: UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        return format_response(404, "Usuario No Encontrado")

    # Update only the provided fields
    if user_data.username:
        existing_user.username = user_data.username
    if user_data.email:
        existing_user.email = user_data.email
    if user_data.role:
        existing_user.role = user_data.role
    if user_data.name:
        existing_user.name = user_data.name        
    if user_data.status:
        existing_user.status = user_data.status

    db.commit()
    db.refresh(existing_user)

    user_data_response = {
        "id": existing_user.id,
        "username": existing_user.username,
        "email": existing_user.email,
        "role": existing_user.role,
        "name": existing_user.name,
        "status": existing_user.status
    }

    return format_response(200, "Usuario actualizado exitosamente", user_data_response)


@router.get("/userDetails", summary="Retrieve a user by ID or username")
def get_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_id: int = Query(None, description="Filter user by ID"),
    username: str = Query(None, description="Filter user by username"),
):
    try:
        query = db.query(User)

        if user_id:
            query = query.filter(User.id == user_id)
        if username:
            query = query.filter(User.username == username)

        user = query.first()

        if not user:
            return format_response(404, "No se encontró el usuario")

        user_data = {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }

        return format_response(200, "Usuario encontrado exitosamente", user_data)

    except Exception as e:
        print(e)
        return format_response(500, "Error interno del servidor")
    
    
    
    
@router.delete("/users/{user_id}", response_model=dict)
def delete_waitlist(user_id: int, db: Session = Depends(get_db)):
    try:
        existing_entry = db.query(User).filter(User.id == user_id).first()

        if not existing_entry:
            return format_response(404, "Usuario no encontrado")

        db.delete(existing_entry)
        db.commit()

        return format_response(200, "Usuario eliminado con éxito")

    except Exception as e:
        print(e)
        return format_response(500, "Error interno del servidor")





@router.put("/reset-password", summary="Reset password by username")
def reset_password_by_username(
    password_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)    
):

    try:
        username = password_data.get("username")
        new_password = password_data.get("new_password")

        if not username or not new_password:
            return format_response(400, "Se requiere el nombre de usuario y la nueva contraseña")

        # Fetch user by username
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return format_response(404, "No existe el usuario indicado")

        # Hash and update new password
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        db.refresh(user)

        return format_response(200, "Contraseña actualizada exitosamente")

    except Exception as e:
        print(e)
        return format_response(500, "Error interno del servidor")