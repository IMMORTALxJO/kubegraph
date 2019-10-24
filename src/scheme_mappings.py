#!/usr/bin/env python3

NAMES_TO_SCHEMES = {
    # Relational databases
    "mysql": ["mysql"],
    "pgsql": ["postgre", "pgsql"],
    "vertica": ["vertica"],

    # NoSQL databases
    "mongodb": ["mongo", "document_db", "docdb", "documentdb"],
    "elastic": ["elastic"],
    "cassandra": ["cassandra"],
    "dynamodb": ["dynamodb"],

    # Timeserias databases
    "influxdb": ["influx"],
    "clickhouse": ["clickhouse"],

    # Key-Value or Cache databases
    "redis": ["redis"],
    "memcache": ["memcache"],
    "aerospike": ["aerospike"],

    # Queues
    "rabbitmq": ["rabbit"],
    "kafka": ["kafka"],
    "zoo": ["zoo"]
}

PORTS_TO_SCHEMES = {
    # Relational databases
    "3306": "mysql",
    "5432": "pgsql",

    # NoSQL databases
    "27017": "mongodb",
    "9042": "cassandra",
    "9200": "elastic",

    # Timeserias databases
    "8086": "influxdb",

    # Key-Value or Cache databases
    "6379": "redis",
    "11211": "memcache",
    "3000": "aerospike",

    # Queues
    "5672": "rabbitmq",
    "9092": "kafka",
    "9094": "kafka",  # TLS
    "2181": "zoo",

    # WEB
    "80": "http",
    "443": "https"
}

SCHEMES_TO_PORTS = {
    scheme: int(port)
    for port, scheme in PORTS_TO_SCHEMES.items()
}
