from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

SECRET_KEY = "dev-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Get user from token
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"id": user_id, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Role-based access
def require_role(allowed_roles: list):
    def wrapper(current_user=Depends(get_current_user)):
        print("current role:", current_user["role"])
        print("allowed roles:", allowed_roles)
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource"
            )
        return current_user
    return wrapper
