from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from jose import jwt, JWTError
from datetime import datetime, timezone
from loguru import logger

from reachout.src.schemas.auth import ManagerCreate
from reachout.src.models.user import Manager
from reachout.src.core.security import get_passwod_hash, verify_password, create_access_token
from reachout.src.core.config import settings

from reachout.src.core.exeptions import UserExistError, IvalidLoginPasswordError, InvalidTokenError


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def manager_register(self, manager_in: ManagerCreate):
        logger.info(f"Запущена регистрация нового менеджера с email: {manager_in.email}")

        query = select(Manager).filter(Manager.email == manager_in.email)
        result = await self.db.execute(query)
        exist_manager = result.scalar_one_or_none()
        
        if exist_manager:
            logger.warning(f"Менеджера {manager_in.email} не существует")

            raise UserExistError()
    
        new_manager = Manager(
            email=manager_in.email,
            hashed_password=get_passwod_hash(manager_in.password),
            is_active=True
        )
    
        self.db.add(new_manager)
        await self.db.commit()
        await self.db.refresh(new_manager)

        logger.success(f"Менеджер успешно создан. Присвоен ID: {new_manager.id}")
        return new_manager


    async def manager_login(self, manager_in: OAuth2PasswordRequestForm):
        logger.info(f"Попытка входа для пользователя: {manager_in.username}")

        query = select(Manager).filter(Manager.email == manager_in.username)
        result = await self.db.execute(query)
        manager = result.scalar_one_or_none()
            
        if not manager or not verify_password(manager_in.password, manager.hashed_password):
            logger.warning("Неудачная попытка входа: неверный пароль или email для пользователя {login_data.username}")

            raise IvalidLoginPasswordError()

        access_token = create_access_token(
            {
                "sub": manager.email,
                "role": "manager"
            }
        )

        logger.success(f"Успешный вход пользователя: {manager_in.username}")
    
        return {"access_token": access_token, "token_type": "bearer"}


    async def manager_logout(self, token: str, redis_cli: Redis, manager_id: int):
        logger.info(f"Менеджер ID: {manager_id} инициировал выход из системы")

        try:    
            payload = jwt.decode(token=token, key=settings.SECRET_KEY, algorithms=settings.ALGORITHM)

            jti: str | None = payload.get("jti")
            exp: int | None = payload.get("exp")
    
        except JWTError:
            logger.warning(f"Ошибка декодирования токена")
            
            raise InvalidTokenError()
    
        current_time = int(datetime.now(timezone.utc).timestamp())
        remainig_seconds = exp - current_time
    
        if remainig_seconds > 0:
            await redis_cli.set(
                f"blacklist:{jti}",
                value="revoked",
                ex=remainig_seconds
            )

        logger.success(f"Токен jti: {jti} успешно занесен в блэклист Redis. Сессия закрыта.")

        return {"detail": "Successfully logged out. Session terminated safely."}