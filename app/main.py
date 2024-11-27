from pathlib import Path

from oso_cloud import Oso

from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


from app.model.user import User
from app.model.application import Application
from app.model.movie import Movie

from app.model.actions import actions
from app.model.roles import roles

from app.exceptions import *


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path.cwd()/'.env', env_file_encoding='utf-8')

    oso_cloud_api_key: str


settings = Settings()


oso = Oso(url='https://cloud.osohq.com', api_key=settings.oso_cloud_api_key)
oso_application = Application()


def push_policy_to_cloud(oso: Oso, policy_path: str):
    oso.policy(open(policy_path, 'r').read())

push_policy_to_cloud(oso, './main.polar')


nl = '\n' # a hack to insert backslashes in f-strings
description = f'''
Service for authorization

Send a request to `/can-user-{{action}}-movie/{{user_id}}/{{movie_id}}` to check if user with
`user_id` can perform an action on movie with `movie_id`

`action` list:
{''.join(map(lambda action: f'- {action}{nl}', actions))}

## DEV

> This portion of a service will later read a message queue for role setting and movie adding

Right now you can add a role to a user with `user_id` at `/set-user-role/{{user_id}}/{{role}}`

`role` list:
{''.join(map(lambda role: f'- {role}{nl}', roles))}
'''

app = FastAPI(
    title='Authorization Service',
    description=description,
)


@app.get('/can-user-{action}-movie/{user_id}/{movie_id}')
async def check_user_action_on_movie(action: str, user_id: int, movie_id: int):
    if not action in actions: raise ActionNotFoundException
    authorize = oso.authorize(User(id=user_id), action, Movie(id=movie_id))
    if not authorize: raise ForbiddenException



# TODO: move all setters to reading a message queue (kafka)
@app.post('/set-movie-as-free/{movie_id}')
async def set_movie_as_free(movie_id: int):
    oso.insert(('is_free', Movie(id=movie_id), True))

@app.post('/set-user-role/{user_id}/{role}')
async def set_user_role(user_id: int, role: str):
    if role not in roles: raise RoleNotFoundException
    oso.insert(('has_role', User(id=user_id), role, oso_application))
