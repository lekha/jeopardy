"""
Add team and game models
"""
from yoyo import step


__depends__ = {'20200621_01_04gFZ-init-database-schema'}


create_games = """
CREATE TABLE games (
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(4) NOT NULL UNIQUE,
    max_teams INT NOT NULL,
    max_players_per_team INT NOT NULL,
    is_active BOOL NOT NULL DEFAULT 0,
    owner_id BIGINT NOT NULL,
    CONSTRAINT fk_games_players FOREIGN KEY (owner_id) REFERENCES players (id) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
"""

create_teams = """
CREATE TABLE teams (
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    name VARCHAR(255) NOT NULL,
    game_id BIGINT NOT NULL,
    UNIQUE KEY unique_game_id_team_name (game_id, name),
    CONSTRAINT fk_teams_games FOREIGN KEY (game_id) REFERENCES games (id) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
"""


drop_games = "DROP TABLE games;"
drop_teams = "DROP TABLE teams;"


steps = [
    step(create_games, drop_games),
    step(create_teams, drop_teams),
]
