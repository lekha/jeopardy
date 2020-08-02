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


steps = [
    step(add_score, drop_score),
]
