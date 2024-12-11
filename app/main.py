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
    kafka_bootstrap_server: str
    event_bus_topic_name: str


settings = Settings()


oso = Oso(url='https://cloud.osohq.com', api_key=settings.oso_cloud_api_key)
oso_application = Application()

def push_policy_to_cloud(oso: Oso, policy_path: str):
    oso.policy(open(policy_path, 'r').read())

push_policy_to_cloud(oso, './main.polar')



from threading import Thread
from queue import Queue

from kafka import KafkaConsumer

from app.events import Event, Microservice, EventType
from app.kafka_reader import KafkaEventReader



class EventReader(Microservice):
    '''
    '''

    def __init__(self, event_queue: Queue):
        return super().__init__(event_queue)

    def handle_event(self, event: Event):
        '''
        Обработка ивентов
        '''
        target_function = None

        match event.type:
            case EventType.SetMovieFree:
                target_function = self.handle_event_set_movie_free
            case EventType.SetMoviePaid:
                target_function = self.handle_event_set_movie_paid
            case EventType.SetUserRole:
                target_function = self.handle_event_set_user_role
            case _:
                pass

        if target_function is not None:
            Thread(target=target_function, args=event.data).start()

    def handle_event_set_movie_free(self, movie_id: int):
        oso.insert(('is_free', Movie(id=movie_id), True))
    
    def handle_event_set_movie_paid(self, movie_id: int):
        oso.delete(('is_free', Movie(id=movie_id), True))

    def handle_event_set_user_role(self, user_id: int, role: str):
        if role not in roles: raise RoleNotFoundException
        oso.insert(('has_role', User(id=user_id), role, oso_application))


nl = '\n' # a hack to insert backslashes in f-strings
description = f'''
Service for authorization

Send a request to `/can-user-{{action}}-movie/{{user_id}}/{{movie_id}}` to check if user with
`user_id` can perform an action on movie with `movie_id`

`action` list:
{''.join(map(lambda action: f'- {action}{nl}', actions))}

The service is reading *"events"* from a topic `{settings.event_bus_topic_name}` for setting user roles and changing movie freeness

`event` list:
- `smfr {{movie_id}}` - set movie with `movie_id` free
- `smpa {{movie_id}}` - set movie with `movie_id` paid
- `suro {{user_id}} {{role_name}}` - set user with `user_id` role `role_name`

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



eq = Queue()

kafka_event_reader = KafkaEventReader(
    KafkaConsumer(
        settings.event_bus_topic_name,
        bootstrap_servers=settings.kafka_bootstrap_server,
        auto_offset_reset='latest',
    ),
    eq
)

event_reader = EventReader(eq)

# event_reader.running_thread.join()