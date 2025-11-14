from fastapi import Depends
from .users import admin_only
async def admin_required(current=Depends(admin_only)):
    return current
