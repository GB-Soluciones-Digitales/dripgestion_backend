from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.schemas.user import UserUpdate

def get_user_by_username(db: Session, username: str, tenant_id: int):
    return db.query(User).filter(User.username == username, User.tenant_id == tenant_id).first()

def get_users_by_tenant(db: Session, tenant_id: int):
    return db.query(User).filter(User.tenant_id == tenant_id, User.role != UserRole.CLIENTE).all()

def create_user_within_tenant(db: Session, user_in, tenant_id: int):
    db_user = User(
        username=user_in.username,
        full_name=user_in.full_name,
        password=get_password_hash(user_in.password),
        role=user_in.role,
        tenant_id=tenant_id,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_within_tenant(db: Session, user_id: int, user_in: UserUpdate, tenant_id: int):
    db_user = db.query(User).filter(User.id == user_id, User.tenant_id == tenant_id).first()
    if not db_user:
        return None

    update_data = user_in.model_dump(exclude_unset=True) 
    
    if "password" in update_data and update_data["password"]:
        update_data["password"] = get_password_hash(update_data["password"])
    
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int, tenant_id: int):
    user = db.query(User).filter(User.id == user_id, User.tenant_id == tenant_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user