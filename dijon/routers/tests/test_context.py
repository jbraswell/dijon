from datetime import datetime, timedelta
from unittest.mock import patch

from dijon import crud
from dijon.conftest import Ctx
from dijon.dependencies import Context
from dijon.token_util import create_access_token


def test_context_token_non_admin_valid(ctx: Ctx):
    db_user = crud.create_user(ctx.db, "username", "contexttest@jrb.lol", "securepassword")
    access_token = create_access_token(ctx.db, db_user)
    context = Context(token=access_token, db=ctx.db)
    assert context.token == access_token
    assert context.is_authenticated
    assert not context.is_admin
    assert context.user


def test_context_token_non_admin_invalid_user(ctx: Ctx):
    db_user = crud.create_user(ctx.db, "username", "contexttest@jrb.lol", "securepassword")
    access_token = create_access_token(ctx.db, db_user)
    crud.delete_user(ctx.db, db_user.id)
    context = Context(token=access_token, db=ctx.db)
    assert context.token is None
    assert not context.is_authenticated
    assert not context.is_admin
    assert not context.user


def test_context_token_non_admin_inactive_user(ctx: Ctx):
    db_user = crud.create_user(ctx.db, "username", "contexttest@jrb.lol", "securepassword")
    crud.update_user(ctx.db, db_user.id, is_active=False)
    access_token = create_access_token(ctx.db, db_user)
    context = Context(token=access_token, db=ctx.db)
    assert context.token is None
    assert not context.is_authenticated
    assert not context.is_admin
    assert not context.user


def test_context_token_admin(ctx: Ctx):
    db_user = crud.create_user(ctx.db, "username", "contexttest@jrb.lol", "securepassword", is_admin=True)
    access_token = create_access_token(ctx.db, db_user)
    context = Context(token=access_token, db=ctx.db)
    assert context.token == access_token
    assert context.is_authenticated
    assert context.is_admin
    assert context.user == db_user


def test_context_token_admin_inactive(ctx: Ctx):
    db_user = crud.create_user(ctx.db, "username", "contexttest@jrb.lol", "securepassword", is_admin=True)
    crud.update_user(ctx.db, db_user.id, is_active=False)
    access_token = create_access_token(ctx.db, db_user)
    context = Context(token=access_token, db=ctx.db)
    assert context.token is None
    assert not context.is_authenticated
    assert not context.is_admin
    assert not context.user


def test_context_token_invalid_token(ctx: Ctx):
    context = Context(token="blah", db=ctx.db)
    assert context.token is None
    assert not context.is_authenticated
    assert not context.is_admin
    assert not context.user


def test_context_token_invalid_signature(ctx: Ctx):
    db_user = crud.create_user(ctx.db, "username", "contexttest@jrb.lol", "securepassword")
    access_token = create_access_token(ctx.db, db_user)
    access_token += "asdf"
    context = Context(token=access_token, db=ctx.db)
    assert context.token is None
    assert not context.is_authenticated
    assert not context.is_admin
    assert not context.user


def test_context_token_expired(ctx, monkeypatch):
    db_user = crud.create_user(ctx.db, "username", "contexttest@jrb.lol", "securepassword")
    with patch("dijon.token_util.get_access_token_expiration_delta", autospec=True) as get_timedelta:
        get_timedelta.return_value = datetime.utcnow() - timedelta(hours=1)
        access_token = create_access_token(ctx.db, db_user)
    context = Context(token=access_token, db=ctx.db)
    assert context.token is None
    assert not context.is_authenticated
    assert not context.is_admin
    assert not context.user
