"""
Add actions
"""
from yoyo import step


__depends__ = {'20200711_01_mmRoW-add-game-metadata'}


create_choice = """
CREATE TABLE action_choices (
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    game_id BIGINT NOT NULL,
    tile_id BIGINT NOT NULL,
    team_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    CONSTRAINT fk_game_choice FOREIGN KEY (game_id) REFERENCES games (id) ON DELETE CASCADE,
    CONSTRAINT fk_tile_choice FOREIGN KEY (tile_id) REFERENCES tiles (id) ON DELETE CASCADE,
    CONSTRAINT fk_team_choice FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE,
    CONSTRAINT fk_user_choice FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    UNIQUE KEY unique_game_tile (game_id, tile_id)
)
"""


create_buzz = """
CREATE TABLE action_buzzes (
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    game_id BIGINT NOT NULL,
    tile_id BIGINT NOT NULL,
    team_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    CONSTRAINT fk_game_buzzes FOREIGN KEY (game_id) REFERENCES games (id) ON DELETE CASCADE,
    CONSTRAINT fk_tile_buzzes FOREIGN KEY (tile_id) REFERENCES tiles (id) ON DELETE CASCADE,
    CONSTRAINT fk_team_buzzes FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE,
    CONSTRAINT fk_user_buzzes FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    UNIQUE KEY unique_game_tile_team (game_id, tile_id, team_id)
)
"""


create_response = """
CREATE TABLE action_responses (
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    game_id BIGINT NOT NULL,
    tile_id BIGINT NOT NULL,
    team_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    is_correct TINYINT(1) NOT NULL,
    CONSTRAINT fk_game_response FOREIGN KEY (game_id) REFERENCES games (id) ON DELETE CASCADE,
    CONSTRAINT fk_tile_response FOREIGN KEY (tile_id) REFERENCES tiles (id) ON DELETE CASCADE,
    CONSTRAINT fk_team_response FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE,
    CONSTRAINT fk_user_response FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    UNIQUE KEY unique_game_tile_team (game_id, tile_id, team_id)
)
"""


create_wager = """
CREATE TABLE action_wagers (
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    game_id BIGINT NOT NULL,
    tile_id BIGINT NOT NULL,
    team_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    amount INT(11) NOT NULL,
    CONSTRAINT fk_game_wager FOREIGN KEY (game_id) REFERENCES games (id) ON DELETE CASCADE,
    CONSTRAINT fk_tile_wager FOREIGN KEY (tile_id) REFERENCES tiles (id) ON DELETE CASCADE,
    CONSTRAINT fk_team_wager FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE,
    CONSTRAINT fk_user_wager FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    UNIQUE KEY unique_game_tile_team (game_id, tile_id, team_id)
)
"""


drop_choice   = "DROP TABLE action_choices"
drop_buzz     = "DROP TABLE action_buzzes"
drop_response = "DROP TABLE action_responses"
drop_wager    = "DROP TABLE action_wagers"


steps = [
    step(create_choice,   drop_choice),
    step(create_buzz,     drop_buzz),
    step(create_response, drop_response),
    step(create_wager   , drop_wager),
]
