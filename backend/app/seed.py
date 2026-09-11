"""
Seeds the database with a demo course/topic and a demo student so the
frontend has something to show immediately after setup.

Run with:
    python -m app.seed
"""
from app.database import SessionLocal, Base, engine
from app import models
from app.security import hash_password

Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()
    try:
        if db.query(models.Course).first():
            print("Data already exists, skipping seed.")
            return

        course = models.Course(
            title="Python Programming Fundamentals",
            description="Core Python concepts from variables to object-oriented programming.",
            subject="Computer Science",
        )
        db.add(course)
        db.flush()

        topics = [
            models.Topic(course_id=course.id, title="Variables & Data Types", order_index=1,
                         summary="Numbers, strings, booleans, and type conversion in Python."),
            models.Topic(course_id=course.id, title="Control Flow", order_index=2,
                         summary="if/elif/else, loops, and boolean logic."),
            models.Topic(course_id=course.id, title="Functions", order_index=3,
                         summary="Defining functions, parameters, return values, and scope."),
        ]
        db.add_all(topics)

        student = models.Student(
            full_name="Demo Student",
            email="demo@student.com",
            hashed_password=hash_password("demo1234"),
        )
        db.add(student)

        db.commit()
        print(f"Seeded course '{course.title}' (id={course.id}) with {len(topics)} topics.")
        print(f"Seeded demo student: demo@student.com / demo1234 (id={student.id})")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
