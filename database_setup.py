from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
import os

DATABASE_URL = "sqlite:///./perfume_app.db"

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    weight = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    sex = Column(String, nullable=True)
    style = Column(String, nullable=True)
    race = Column(String, nullable=True)
    first_login_completed = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    # Relationships
    perfumes = relationship("UserPerfume", back_populates="user")
    conversation_history = relationship("ConversationHistory", back_populates="user", uselist=False)

class UserPerfume(Base):
    __tablename__ = "user_perfumes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    perfume_name = Column(String, nullable=False)
    # Relationships
    user = relationship("User", back_populates="perfumes")

class PerfumeNote(Base):
    __tablename__ = "perfume_notes"
    id = Column(Integer, primary_key=True, index=True)
    perfume_name = Column(String, unique=True, index=True, nullable=False)
    # Storing notes as JSON. Adjust if a more structured approach is needed.
    # Example: {"top": ["note1", "note2"], "middle": ["note3"], "base": ["note4"]}
    notes_json = Column(JSON, nullable=True)

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    source_url = Column(String, unique=True, nullable=False)

class ConversationHistory(Base):
    __tablename__ = "conversation_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False) # One-to-one with User
    # Storing history as JSON array of messages.
    # Example: [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]
    history_json = Column(JSON, nullable=True, default=[])
    # Relationships
    user = relationship("User", back_populates="conversation_history")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) # check_same_thread for SQLite

def create_db_and_tables():
    # Create all tables in the engine. This is equivalent to "Create Table"
    # statements in raw SQL.
    Base.metadata.create_all(bind=engine)
    print("Database and tables created successfully.")

if __name__ == "__main__":
    create_db_and_tables()
    # You can add some initial data here for testing if needed
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    # Example: Create a dummy perfume note if it doesn't exist
    existing_note = db.query(PerfumeNote).filter(PerfumeNote.perfume_name == "Dior Sauvage").first()
    if not existing_note:
        new_note = PerfumeNote(
            perfume_name="Dior Sauvage",
            notes_json={"top": ["Bergamot", "Pepper"], "middle": ["Sichuan Pepper", "Geranium"], "base": ["Ambroxan", "Cedar"]}
        )
        db.add(new_note)
        db.commit()
        print("Added dummy Dior Sauvage note.")
    db.close()
