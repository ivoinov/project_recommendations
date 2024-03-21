import pytest
from sqlalchemy.orm import declarative_base
from app.models import Base


def test_base_instance():
    assert isinstance(
        Base, type(declarative_base())
    ), "Base should be an instance of declarative_base"


def test_base_has_metadata():
    assert hasattr(Base, "metadata"), "Base should have a metadata attribute"
