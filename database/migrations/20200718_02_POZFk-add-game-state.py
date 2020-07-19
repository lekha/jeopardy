"""
Add game state
"""
from yoyo import step


__depends__ = {'20200718_01_FIfKc-add-actions'}


add_game_state = """
ALTER TABLE games
DROP COLUMN is_active,
 ADD COLUMN is_started BOOL NOT NULL DEFAULT 0,
 ADD COLUMN is_finished BOOL NOT NULL DEFAULT 0,
 ADD COLUMN next_message_id INT(11),
 ADD COLUMN next_round_id BIGINT,
 ADD COLUMN next_action_type ENUM("buzz", "choice", "response", "wager"),
 ADD COLUMN next_chooser_id BIGINT,
 ADD CONSTRAINT fk_next_chooser_team FOREIGN KEY (next_chooser_id) REFERENCES teams (id) ON DELETE RESTRICT,
 ADD CONSTRAINT fk_next_round FOREIGN KEY (next_round_id) REFERENCES rounds (id) ON DELETE RESTRICT
"""


drop_game_state = """
ALTER TABLE games
DROP FOREIGN KEY fk_next_chooser_team,
DROP FOREIGN KEY fk_next_round,
DROP COLUMN is_started,
DROP COLUMN is_finished,
DROP COLUMN next_message_id,
DROP COLUMN next_round_id,
DROP COLUMN next_action_type,
DROP COLUMN next_chooser_id,
 ADD COLUMN is_active BOOL NOT NULL DEFAULT 0
"""


steps = [
    step(add_game_state, drop_game_state),
]
