from app.models.taxi_trip import Base
from app.db.database import engine

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")