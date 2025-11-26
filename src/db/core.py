from .models import Base
from .database import sync_engine

def create_tables():
    # Base.metadata.drop_all(sync_engine)
    Base.metadata.create_all(sync_engine)