import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..core.db import get_db

router = APIRouter(prefix="/api", tags=["9_shape"])
logger = logging.getLogger()

@router.get("/9-shape/match")
def get_9_shape_matches(
    shape: int,
    db: Session = Depends(get_db)
  ):
    try:  
        stmt = text('SELECT * FROM raw_linescores WHERE "9_shape" = :shape')
        rows = db.execute(stmt, {"shape": shape}).fetchall()
        return [dict(r._mapping) for r in rows]
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f'Failure in GET /9-shape/match: {str(e)}')
        raise HTTPException(status_code=400, detail=str(e))
