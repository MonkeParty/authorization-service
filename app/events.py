from enum import Enum

from queue import Queue

import threading
from threading import Thread


class EventType(Enum):
    Invalid = 'erro'

    SetMovieFree = 'smfr'

    SetMoviePaid = 'smpa'

    SetUserRole = 'suro'



_event_type_members = EventType._member_map_.values()
class EventTypeConstants:
    event_type_to_prefix = {}
    prefix_to_event_type = {}

    for enum in _event_type_members:
        event_type_to_prefix[enum] = enum.value
        prefix_to_event_type[enum.value] = enum


class Event:
    def __init__(self, type: EventType, data):
        self.type = type
        self.data = data

    def __str__(self) -> str:
        return f'{EventTypeConstants.event_type_to_prefix[self.type]} {self.data}'


def get_role_set(data: str):
    user_id, name = data.split()
    return int(user_id), name

def get_movie_id(data: str):
    return (int(data),)

class EventFromMessage(Event):
    def __init__(self, kafka_message: str):
        prefix = kafka_message[:4]
        data = kafka_message[5:]

        try:
            event_type = EventTypeConstants.prefix_to_event_type[prefix]
        except:
            event_type = EventType.Invalid

        match event_type:
            case EventType.SetUserRole:
                data = get_role_set(data)
            case EventType.SetMovieFree:
                data = get_movie_id(data)
            case EventType.SetMoviePaid:
                data = get_movie_id(data)
            case _:
                data = f'Error: got invalid message: {kafka_message}'

        return super().__init__(event_type, data)



import time


class Microservice:
    '''
    Абстрактный класс микросервиса
    Все микросервисы должны его наследовать
    Для него должна быть реализована функция `self.handle_event(event: Event)`
    '''

    DEFAULT_QUEUE_CHECK_TIMER = 10.0
    MINIMAL_QUEUE_CHECK_TIMER = 0.5

    def __init__(self, event_queue: Queue):
        '''
        Инициализация класса:
        - `event_queue` - очередь приходящих событий
        - `writers` - словарь, где ключ - название микросервиса, значение - писатель событий в этот микросервис
        Поля класса:
        - `self.event_queue` - очередь приходящих событий
        - `self.writers` - словарь, где ключ - название микросервиса, значение - писатель событий в этот микросервис
        - `self.queue_check_timer` - кол-во секунд ожидаемое перед каждой проверкой очереди событий
        - `self.running` - мультипоточное булевое значение, указывающее состояние микросервиса
        - `self.runnning_thread` - указатель на поток, в котором запущен микросервис 
        '''

        self.event_queue = event_queue

        self.queue_check_timer = self.DEFAULT_QUEUE_CHECK_TIMER

        self.running = threading.Event()
        self.running.set()

        self.running_thread = Thread(target=self.run)
        self.running_thread.start()

    def set_queue_check_timer(self, seconds: float):
        self.queue_check_timer = max(seconds, self.MINIMAL_QUEUE_CHECK_TIMER)

    def run(self):
        '''
        Принятие событий из очереди 
        '''

        while self.running.is_set():

            if self.event_queue.empty():
                time.sleep(self.queue_check_timer)
                continue

            self.handle_event(self.event_queue.get())

    '''
    Пример реализуемого функционала микросервиса:
    def handle_event(self, event: Event):
        match event.type:
            case EventType.TrendData:
                self.handle_event_trend_data(event.data)
            case EventType.TrendAnalyseResult:
                self.handle_event_trend_analyse_result(event.data)
            case _:
                pass

    def handle_event_trend_data(self, trend_data: TrendData):
        self.dm_ai_event_writer.send_event(Event(EventType.TrendData, trend_data))

    def handle_event_trend_analyse_result(self, scale_data: ScaleData):
        deployment = self.k8s_api.read_namespaced_deployment(self.target_deployment, self.target_namespace)
        deployment.spec.replicas = scale_data.replica_count
        _api_response = self.k8s_api.patch_namespaced_deployment(
            name=self.target_deployment,
            namespace=self.target_namespace,
            body=deployment
        )
    '''

    def stop(self):
        self.running.clear()
        self.running_thread.join()
