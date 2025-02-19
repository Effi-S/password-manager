from pathlib import Path

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

_PDB = Path(__file__).parent / ".passwords.db"
Base = declarative_base()


class Password(Base):
    __tablename__ = "passwords"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    username = Column(String, nullable=True)
    encrypted_password = Column(String, nullable=False)


engine = create_engine(f"sqlite:///{_PDB}")
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def get_test_session():
    test_engine = create_engine(f"sqlite:///{_PDB}.test")
    test_Session = sessionmaker(bind=test_engine)
    Base.metadata.create_all(test_engine)
    return test_Session()
