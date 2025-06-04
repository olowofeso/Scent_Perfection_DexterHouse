# create_admin.py
import argparse
from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, DATABASE_URL # Assuming DATABASE_URL is defined in database_setup

def create_or_update_admin(db_session, email, password):
    user = db_session.query(User).filter_by(email=email).first()
    hashed_password = generate_password_hash(password)

    if user:
        print(f"Updating existing user: {email}")
        user.password_hash = hashed_password
        user.is_admin = True
        user.first_login_completed = True # Admin skips first time flow
    else:
        print(f"Creating new admin user: {email}")
        user = User(
            email=email,
            password_hash=hashed_password,
            is_admin=True,
            first_login_completed=True
        )
        db_session.add(user)

    try:
        db_session.commit()
        print(f"Admin user {email} processed successfully.")
    except Exception as e:
        db_session.rollback()
        print(f"Error processing admin user {email}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create or update an admin user.")
    parser.add_argument("email", type=str, help="Admin user's email address")
    parser.add_argument("password", type=str, help="Admin user's password")
    args = parser.parse_args()

    engine = create_engine(DATABASE_URL)
    Base.metadata.bind = engine # Ensure Base is bound if not already

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    create_or_update_admin(session, args.email, args.password)

    session.close()
