from pathlib import Path

from oso_cloud import Oso

from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


from app.model.system import System
from app.model.user import User
from app.model.application import Application
from app.model.movie import Movie
from app.model.roles import roles
from app.exceptions import *


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path.cwd()/'.env', env_file_encoding='utf-8')

    oso_cloud_api_key: str


settings = Settings()


oso = Oso(url='https://cloud.osohq.com', api_key=settings.oso_cloud_api_key)
oso_system = System()
oso_application = Application()


def push_policy_to_cloud(oso: Oso, policy_path: str):
    oso.policy(open(policy_path, 'r').read())

push_policy_to_cloud(oso, './policy.polar')



app = FastAPI()


@app.get('/can-user-view-movie/{user_id}/{movie_id}')
async def can_user_view_movie(user_id: int, movie_id: int):
    can_view = oso.authorize(User(id=user_id), 'view', Movie(id=movie_id))
    if can_view: return

    can_view_for_free = oso.authorize(User(id=user_id), 'view-partial', Movie(id=movie_id))
    if not can_view_for_free:
        raise ForbiddenException

@app.get('/can-user-edit-movie/{user_id}/{movie_id}')
async def can_user_edit_movie(user_id: int, movie_id: int):
    can_edit = oso.authorize(User(id=user_id), 'edit', Movie(id=movie_id))
    if not can_edit:
        raise ForbiddenException


# TODO: move all setters to reading a message queue (kafka)
@app.post('/set-movie-as-free/{movie_id}')
async def set_movie_as_free(movie_id: int):
    oso.insert(('has_role', oso_system, 'free-movie', Movie(id=movie_id)))

@app.post('/set-user-role/{user_id}/{role}')
async def set_user_role(user_id: int, role: str):
    print(role, roles)
    if role not in roles:
        raise RoleNotFoundException
    oso.insert(('has_role', User(id=user_id), role, oso_application))
