import random
import string

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from api.models import Base, engine, User, SessionLocal
from api.views import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


fake_email = ''.join(random.choice(string.ascii_letters) for _ in range(7)) + "@gmail.com"


def test_registration():
    response = client.post(
        "/registration",
        json={"email": fake_email, "password": "pass", "phone_number": "0555555"},
    )
    assert response.status_code == 201

