# authorization-service
# How to run
```sh
py -m pip install -r requirements.txt
OSO_CLOUD_API_KEY=<your_api_key> KAFKA_BOOTSTRAP_SERVER=<kafka_server> EVENT_BUS_TOPIC_NAME=<event_topic> uvicorn app.main:app --reload
```
