from sqlalchemy import or_
from database.db import get_db
from database.models import UserProgress


def fix_null_progress():
    db = next(get_db())
    try:

        null_records = db.query(UserProgress).filter(
            or_(
                UserProgress.correct_answers == None,
                UserProgress.wrong_answers == None
            )
        )
        updated = null_records.update({
            UserProgress.correct_answers: 0,
            UserProgress.wrong_answers: 0
        }, synchronize_session=False)

        db.commit()
        return updated
    except Exception as e:
        db.rollback()
        print(e)
        raise
    finally:
        db.close()