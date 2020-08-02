"""
Add score and game state
"""
from yoyo import step


__depends__ = {'20200719_01_SJdgK-add-team-membership'}


add_score = """
ALTER TABLE teams
 ADD COLUMN score INT(11) NOT NULL DEFAULT 0
"""


drop_score = """
ALTER TABLE teams
DROP COLUMN score
"""


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


drop_game_state = "DROP TABLE game_states"


steps = [
    step(add_score, drop_score),
    step(add_game_state, drop_game_state),
]
