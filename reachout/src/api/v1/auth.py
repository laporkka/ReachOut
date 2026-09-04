from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from reachout.src.schemas.auth import Token, ManagerCreate, ManagerResponse
from reachout.src.models.user import Manager
from reachout.src.core.database import get_db
from reachout.src.core.security import get_passwod_hash, verify_password, create_access_token


router = APIRouter(prefix="/managers", tags=["Managers"])


@router.post("/register", response_model=ManagerResponse, status_code=status.HTTP_201_CREATED)
async def manager_register(
    manager_in: ManagerCreate,
    db: AsyncSession = Depends(get_db)
):
    query = select(Manager).filter(Manager.email == manager_in.email)
    result = await db.execute(query)
    exist_manager = result.scalar_one_or_none()

    if exist_manager:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exist"
        )

    new_manager = Manager(
        email=manager_in.email,
        hashed_password=get_passwod_hash(manager_in.password),
        is_active=True
    )

    db.add(new_manager)
    await db.commit()
    await db.refresh(new_manager)

    return new_manager


@router.post("/login", response_model=Token, status_code=status.HTTP_201_CREATED)
async def manager_login(
    manager_in: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    query = select(Manager).filter(Manager.email == manager_in.username)
    result = await db.execute(query)
    manager = result.scalar_one_or_none()

    if not manager or not verify_password(manager_in.password, manager.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password"
        )

    access_token = create_access_token(
        {
            "sub": manager.email,
            "role": "manager"
        }
    )

    return {"access_token": access_token, "token_type": "bearer"}