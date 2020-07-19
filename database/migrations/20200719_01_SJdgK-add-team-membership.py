"""
Add team membership
"""
from yoyo import step


__depends__ = {'20200718_02_POZFk-add-game-state'}


add_team_membership = """
CREATE TABLE team_memberships (
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    team_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    CONSTRAINT fk_team_membership FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE RESTRICT,
    CONSTRAINT fk_membership_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE RESTRICT,
    UNIQUE KEY unique_team_user (team_id, user_id),
    KEY idx_user (user_id)
)
"""


drop_team_membership = "DROP TABLE team_memberships"


steps = [
    step(add_team_membership, drop_team_membership),
]
