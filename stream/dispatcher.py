"""Publishes ride/food requests to the topic exchange 'rapido-dispatch'.

Routing key format: city.zone.type   e.g. bangalore.koramangala.food
Every 10th message is deliberately "bad": it has no 'zone' field in the body
(the routing key is still valid), so drivers must NACK it (Part D3).

Usage:
    python dispatcher.py                 # run forever, one message every 2 s
    python dispatcher.py --count 30      # stop after 30 messages
    python dispatcher.py --demo-d1       # publish the 6 routing keys from D1 once
The broker URL comes from the AMQP_URL environment variable (never commit it).
"""
import argparse
import json
import os
import random
import time
import uuid

import pika

EXCHANGE = "rapido-dispatch"
CITIES = ["bangalore", "chennai"]
ZONES = ["koramangala", "indiranagar", "whitefield", "tnagar"]
TYPES = ["ride", "food"]
D1_KEYS = [
    "bangalore.koramangala.food",
    "bangalore.indiranagar.ride",
    "bangalore.whitefield.ride",
    "chennai.tnagar.food",
    "chennai.whitefield.ride",
    "bangalore.koramangala",
]


def connect():
    url = os.environ.get("AMQP_URL", "amqp://guest:guest@localhost:5672/%2F")
    return pika.BlockingConnection(pika.URLParameters(url))


def publish(channel, routing_key, body):
    channel.basic_publish(
        exchange=EXCHANGE,
        routing_key=routing_key,
        body=json.dumps(body),
        properties=pika.BasicProperties(content_type="application/json"),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=0, help="0 = run forever")
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--bad-every", type=int, default=10)
    parser.add_argument("--demo-d1", action="store_true")
    args = parser.parse_args()

    conn = connect()
    ch = conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=False)

    if args.demo_d1:
        for i, key in enumerate(D1_KEYS, 1):
            parts = key.split(".")
            body = {"id": f"D1-{i}", "city": parts[0], "zone": parts[1],
                    "type": parts[2] if len(parts) > 2 else None, "ts": time.time()}
            publish(ch, key, body)
            print(f"[D1 #{i}] published key={key}", flush=True)
            time.sleep(0.5)
        conn.close()
        return

    n = 0
    while args.count == 0 or n < args.count:
        n += 1
        city = random.choice(CITIES)
        zone = random.choice(ZONES)
        kind = random.choice(TYPES)
        key = f"{city}.{zone}.{kind}"
        body = {"id": str(uuid.uuid4())[:8], "city": city, "zone": zone,
                "type": kind, "ts": time.time()}
        bad = args.bad_every and n % args.bad_every == 0
        if bad:
            del body["zone"]                 # bad message: zone field missing
        publish(ch, key, body)
        print(f"#{n:03d} published key={key}" + ("   <-- BAD (no zone)" if bad else ""),
              flush=True)
        time.sleep(args.interval)
    conn.close()


if __name__ == "__main__":
    main()
