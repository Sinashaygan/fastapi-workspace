from core.database import SessionLocal
from faker import Faker
from users.models import UserModel
from tasks.models import TaskModel





def main():
    db = SessionLocal()
    try:
        user = seed_users(db)[0]
        seed_tasks(db, user)
    finally:
        db.close()


if __name__ == "__main__":
    main()