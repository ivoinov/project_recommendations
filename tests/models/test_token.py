from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.models import Token


def test_token_id_column():
    column = Token.id.property.columns[0]
    assert isinstance(column, Column), "Token model should have an 'id' column"
    assert isinstance(column.type, Integer), "'id' column should be of type Integer"
    assert column.primary_key == True, "'id' column should be a primary key"


def test_token_token_column():
    column = Token.token.property.columns[0]
    assert isinstance(column, Column), "Token model should have a 'token' column"
    assert isinstance(column.type, String), "'token' column should be of type String"
    assert column.unique == True, "'token' column should be unique"
    assert column.index == True, "'token' column should be indexed"


def test_token_user_id_column():
    column = Token.user_id.property.columns[0]
    assert isinstance(column, Column), "Token model should have a 'user_id' column"
    assert isinstance(
        column.type, Integer
    ), "'user_id' column should be of type Integer"
    assert column.foreign_keys is not None, "'user_id' column should have a foreign key"


def test_token_user_relationship():
    assert (
        "user" in Token.__mapper__.relationships
    ), "Token model should have a 'user' relationship"


def test_token_expires_at_column():
    column = Token.expires_at.property.columns[0]
    assert isinstance(column, Column), "Token model should have an 'expires_at' column"
    assert isinstance(
        column.type, DateTime
    ), "'expires_at' column should be of type DateTime"
