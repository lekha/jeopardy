"""
Update state
"""
from yoyo import step


__depends__ = {'20200802_01_if48B-add-score-and-game-state'}


drop_game_state = "DROP TABLE game_states"


add_game_state = """
CREATE TABLE game_states(
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    game_id BIGINT NOT NULL,
    full TEXT,
    partial TEXT,
    CONSTRAINT fk_game_state FOREIGN KEY (game_id) REFERENCES games (id) ON DELETE CASCADE
)
"""


add_status = """
ALTER TABLE games
DROP COLUMN is_started,
DROP COLUMN is_finished,
 ADD COLUMN status ENUM("editable", "joinable", "started", "finished") NOT NULL AFTER owner_id
"""


drop_status = """
ALTER TABLE games
DROP COLUMN status,
 ADD COLUMN is_started BOOL NOT NULL DEFAULT 0 AFTER owner_id,
 ADD COLUMN is_finished BOOL NOT NULL DEFAULT 0 AFTER is_started
"""


add_round_reveals = """
CREATE TABLE round_reveals (
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    round_id BIGINT NOT NULL,
    level ENUM("category", "tile"),
    level_id BIGINT NOT NULL,
    detail ENUM("name", "is_daily_double", "answer", "question") NOT NULL,
    CONSTRAINT fk_round_reveal FOREIGN KEY (round_id) REFERENCES rounds (id) ON DELETE CASCADE,
    UNIQUE KEY unique_round_level_detail (round_id, level, level_id, detail)
)
"""


drop_round_reveals = "DROP TABLE round_reveals"


steps = [
    step(drop_game_state, add_game_state),
    step(add_status, drop_status),
    step(add_round_reveals, drop_round_reveals),
]
