"""
Init database schema
"""

from yoyo import step

__depends__ = {}

up_query = """
CREATE TABLE players (
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    name VARCHAR(255) NOT NULL
)
CHARACTER SET utf8mb4;
"""

down_query = """
DROP TABLE players;
"""

steps = [
    step(up_query, down_query)
]
