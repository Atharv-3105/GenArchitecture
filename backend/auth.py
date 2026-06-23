import os 
import logging 
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status 
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

CLERK_ISSUER = os.getenv("CLERK_ISSUER")
if not CLERK_ISSUER:
    raise ValueError("CLERK ISSUER env variable is not set")

#CLERKS public keys endpoint
JWKS_URL = f"{CLERK_ISSUER}/.well-known/jwks.json"
jwks_client = PyJWKClient(JWKS_URL)

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """ 
        Verifies the Clerk JWK Token and return's the User's unique ID
    """
    
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(credentials.credentials)
        
        #Decode and verify the token
        payload = jwt.decode(
            credentials.credentials,
            signing_key.key,
            algorithms=["RS256"],
            issuer=CLERK_ISSUER,
            options={"verify_aud": False}
        )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        return user_id
    
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        