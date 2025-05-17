from database.db import engine, get_db
from database.models import Base, Word
import json


def init_database():

    Base.metadata.create_all(bind=engine)

    with open("database/words.json", "r", encoding="utf-8") as f:
        words = json.load(f)

    db = next(get_db())
    try:
        for word_pair in words:
            if not db.query(Word).filter_by(english=word_pair["english"]).first():
                db.add(Word(
                    english=word_pair["english"],
                    russian=word_pair["russian"]
                ))
        db.commit()
        print("База успешно инициализирована!")

    except Exception as e:
        db.rollback()
        print(f"Ошибка: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    init_database()