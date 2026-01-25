from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import uuid # Needed to validate UUID strings

SECRET_KEY = "dev-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        
        if user_id is None or role is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        
        # Verify the sub is a valid UUID string
        try:
            uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid User ID format")

        return {"id": user_id, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

def require_role(allowed_roles: list):
    # This remains mostly the same, but ensure roles are compared as strings
    def wrapper(current_user=Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource"
            )
        return current_user
    return wrapper