"""
Add game metadata
"""
from yoyo import step


__depends__ = {'20200706_02_A7eKy-rename-user-column'}


create_trivia = """
CREATE TABLE trivia (
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    answer TEXT NOT NULL,
    question TEXT NOT NULL
)
CHARACTER SET utf8mb4;
"""


create_round = """
CREATE TABLE rounds (
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    game_id BIGINT NOT NULL,
    class ENUM("single", "double") NOT NULL,
    categories INT(11) NOT NULL DEFAULT 6,
    tiles_per_category INT(11) NOT NULL DEFAULT 5,
    CONSTRAINT fk_game_round FOREIGN KEY (game_id) REFERENCES games (id) ON DELETE CASCADE,
    UNIQUE KEY unique_game_class (game_id, class)
)
CHARACTER SET utf8mb4;
"""


create_category = """
CREATE TABLE categories (
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    round_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    ordinal INT(11) NOT NULL,
    CONSTRAINT fk_round_category FOREIGN KEY (round_id) REFERENCES rounds (id) ON DELETE CASCADE,
    UNIQUE KEY unique_round_name (round_id, name),
    UNIQUE KEY unique_round_ordinal (round_id, ordinal)
)
CHARACTER SET utf8mb4;
"""


create_tile = """
CREATE TABLE tiles (
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    category_id BIGINT NOT NULL,
    trivia_id BIGINT NOT NULL,
    ordinal INT(11) NOT NULL,
    is_daily_double BOOL NOT NULL DEFAULT 0,
    CONSTRAINT fk_category_tile FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE,
    CONSTRAINT fk_trivia_tile FOREIGN KEY (trivia_id) REFERENCES trivia (id) ON DELETE RESTRICT,
    UNIQUE KEY unique_category_trivia (category_id, trivia_id),
    UNIQUE KEY unique_category_ordinal (category_id, ordinal)
)
CHARACTER SET utf8mb4;
"""


drop_trivia   = "DROP TABLE trivia"
drop_round    = "DROP TABLE rounds"
drop_category = "DROP TABLE categories"
drop_tile     = "DROP TABLE tiles"


steps = [
    step(create_trivia,   drop_trivia),
    step(create_round,    drop_round),
    step(create_category, drop_category),
    step(create_tile,     drop_tile),
]
