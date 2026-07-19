from database.database import engine, Base
from database.model import Document

Base.metadata.create_all(bind=engine)

print("Database Created")