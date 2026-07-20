from database.database import engine, Base
from database.model.document import Document
from database.model.document_image import DocumentImage

Base.metadata.create_all(bind=engine)

print("Database Created")