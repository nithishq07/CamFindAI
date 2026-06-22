import sqlalchemy as sa
from app.core.database import engine
from app.models.base import Base
from app.models.schema import *

with engine.begin() as conn:
    conn.execute(sa.text("DROP TABLE IF EXISTS alembic_version"))
    
Base.metadata.drop_all(bind=engine)
