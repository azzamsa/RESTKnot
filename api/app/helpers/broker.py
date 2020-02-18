import os
import json
from kafka import KafkaProducer
from kafka import KafkaConsumer
from loguru import logger


def get_broker_info():
    host = os.environ.get("KAFKA_HOST")
    port = os.environ.get("KAFKA_PORT")

    broker_address = f"{host}:{port}"
    topic = os.environ.get("RESTKNOT_KAFKA_TOPIC")

    if (host and port) is None:
        raise ValueError("Can't find kafka host and port")

    return broker_address, topic


def kafka_consumer():
    """Create Kafka consumer."""
    broker_address, _ = get_broker_info()

    try:
        consumer = KafkaConsumer(
            "status",
            bootstrap_servers=[broker_address],
            auto_offset_reset="earliest",
            # enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            consumer_timeout_ms=1000,
        )
        return consumer
    except Exception as e:
        raise ValueError(f"{e}")


def kafka_producer():
    """Create Kafka producer."""
    broker_address, _ = get_broker_info()

    producer = KafkaProducer(
        bootstrap_servers=[broker_address],
        value_serializer=lambda m: json.dumps(m).encode("utf-8"),
    )
    return producer


def send(message):
    """Send given message to Kafka broker."""
    producer = None
    try:
        producer = kafka_producer()
        topic = os.environ.get("RESTKNOT_KAFKA_TOPIC")
        producer.send(topic, message)
        producer.flush()
    except Exception as e:
        logger.debug(e)
        raise ValueError(f"{e}")
    finally:
        if producer:
            producer.close()


def take_message():
    messages = []
    consumer = kafka_consumer()

    # consumer.poll()
    # go to end of the stream
    # consumer.seek_to_end()

    for message in consumer:
        messages.append(message.value)

    return messages
    consumer.close()
