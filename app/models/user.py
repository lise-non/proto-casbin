from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# In a real application, you would use SQLAlchemy or another ORM
# This is a simplified in-memory model for demonstration
class User(BaseModel):
    id: str
    email: str
    username: str
    hashed_password: str
    full_name: Optional[str] = None
    role: str
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

# In-memory user database (for demonstration purposes)
users_db = {}