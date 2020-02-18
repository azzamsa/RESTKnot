import os
import json
from kafka import KafkaConsumer
from kafka import KafkaProducer

from dnsagent.libs import utils


def get_broker_info():
    host = os.environ.get("RESTKNOT_KAFKA_BROKER")
    port = os.environ.get("RESTKNOT_KAFKA_PORTS")

    broker_address = f"{host}:{port}"
    topic = os.environ.get("RESTKNOT_KAFKA_TOPIC")

    if (host and port) is None:
        utils.log_err("Can't find kafka host and port")
        exit()

    return broker_address, topic


def kafka_consumer():
    """Create Kafka consumer."""
    broker_address, topic = get_broker_info()

    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=[broker_address],
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
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
        producer.send("status", message)
        producer.flush()
    except Exception as e:
        raise ValueError(f"{e}")
    finally:
        if producer:
            producer.close()
