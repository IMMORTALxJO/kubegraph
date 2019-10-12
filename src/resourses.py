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


def get_scheme_from_name(name):
    """
    Return scheme based on string substrings
        MYSQL_HOST -> mysql
    """
    low_name = str.lower(name)
    for schema, keys in NAMES_TO_SCHEMES.items():
        for key in keys:
            if key in low_name:
                return schema
    return False


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
    "2181": "zoo"
}


def get_scheme_from_port(num):
    """
    Return scheme based on port
        3306 -> mysql
    """
    if num in PORTS_TO_SCHEMES:
        return PORTS_TO_SCHEMES[num]
    return False
