import os

from dnsagent.clis.base import Base
from dnsagent.libs import knot as knot_lib
from dnsagent.libs import broker
from dnsagent.libs import utils


class Start(Base):
    """
        usage:
            start

        Command :

        Options:
        -h --help                             Print usage
    """

    def take_message(self):
        consumer = broker.kafka_consumer()
        agent_type = os.environ.get("RESTKNOT_AGENT_TYPE")

        try:
            for message in consumer:
                message = message.value

                agent_type_msg = message["agent"]["agent_type"]
                if agent_type in agent_type_msg:

                    process_msg = message["process"]
                    knot_queries = message["knot"]
                    for query in knot_queries:
                        knot_lib.execute(query, process_msg)

            consumer.close()

        except KeyboardInterrupt:
            print("Stopping dnsagent. Press Ctrl+C again to exit")

    def execute(self):
        utils.log_info("Starting dnsagent...")
        self.take_message()
