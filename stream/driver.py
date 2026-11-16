"""A driver: binds a private queue to 'rapido-dispatch' with PATTERN.

Usage:  python driver.py NAME PATTERN
        python driver.py Ravi "bangalore.koramangala.*"

'*' matches exactly one word, '#' matches zero or more words.
Messages without a 'zone' field are rejected with basic_nack(requeue=False);
every other message is acknowledged with basic_ack.
"""
import json
import os
import sys

import pika

EXCHANGE = "rapido-dispatch"


def main():
    if len(sys.argv) != 3:
        sys.exit('usage: python driver.py NAME PATTERN')
    name, pattern = sys.argv[1], sys.argv[2]

    url = os.environ.get("AMQP_URL", "amqp://guest:guest@localhost:5672/%2F")
    conn = pika.BlockingConnection(pika.URLParameters(url))
    ch = conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=False)

    # private queue: server-named, exclusive to this connection, deleted on exit
    queue = ch.queue_declare(queue="", exclusive=True).method.queue
    ch.queue_bind(exchange=EXCHANGE, queue=queue, routing_key=pattern)
    print(f"[{name}] bound queue {queue} with pattern '{pattern}'", flush=True)

    def on_message(channel, method, properties, body):
        try:
            msg = json.loads(body)
        except json.JSONDecodeError:
            msg = {}
        if "zone" not in msg:
            print(f"[{name}] NACK (missing zone) key={method.routing_key} body={body.decode()}",
                  flush=True)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return
        print(f"[{name}] got key={method.routing_key} id={msg.get('id')} "
              f"{msg.get('type')} in {msg.get('zone')}", flush=True)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    ch.basic_consume(queue=queue, on_message_callback=on_message, auto_ack=False)
    try:
        ch.start_consuming()
    except KeyboardInterrupt:
        ch.stop_consuming()
    conn.close()


if __name__ == "__main__":
    main()
