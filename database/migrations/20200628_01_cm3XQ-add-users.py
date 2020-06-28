"""
Add users
"""
from yoyo import step


__depends__ = {'20200621_02_tnF6J-add-team-and-game-models'}


create_user_metadata = """
CREATE TABLE user_metadata_anonymous (
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    expire_ts DATETIME(6) NOT NULL
)
CHARACTER SET utf8mb4;

CREATE TABLE user_metadata_google (
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    subject VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    given_name VARCHAR(255),
    issuer VARCHAR(255) NOT NULL,
    family_name VARCHAR(255),
    name VARCHAR(255),
    locale VARCHAR(255),
    picture VARCHAR(255)
)
CHARACTER SET utf8mb4;
"""


drop_user_metadata = """
DROP TABLE user_metadata_google;
DROP TABLE user_metadata_anonymous;
"""


create_users = """
CREATE TABLE users (
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    display_name VARCHAR(255) NOT NULL,
    is_active BOOL NOT NULL DEFAULT 1,
    auth_provider ENUM("none", "google") NOT NULL,
    anonymous_metadata_id BIGINT,
    google_metadata_id BIGINT,
    CONSTRAINT fk_user_anonymous_metadata FOREIGN KEY (anonymous_metadata_id) REFERENCES user_metadata_anonymous (id) ON DELETE RESTRICT,
    CONSTRAINT fk_user_google_metadata FOREIGN KEY (google_metadata_id) REFERENCES user_metadata_google (id) ON DELETE RESTRICT
)
CHARACTER SET utf8mb4;
"""


drop_users = "DROP TABLE users;"


point_foreign_keys_to_users = """
ALTER TABLE games
       DROP FOREIGN KEY fk_games_players,
        ADD CONSTRAINT fk_games_users FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE CASCADE;

DROP TABLE players;
"""


point_foreign_keys_to_players = """
ALTER TABLE games
       DROP FOREIGN KEY fk_games_users;

CREATE TABLE players (
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    name VARCHAR(255) NOT NULL
)
CHARACTER SET utf8mb4;

ALTER TABLE games
        ADD CONSTRAINT fk_games_players FOREIGN KEY (owner_id) REFERENCES players (id) ON DELETE CASCADE;
"""


steps = [
    step(create_user_metadata, drop_user_metadata),
    step(create_users, drop_users),
    step(point_foreign_keys_to_users, point_foreign_keys_to_players),
]
