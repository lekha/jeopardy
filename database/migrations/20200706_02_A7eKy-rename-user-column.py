"""
Rename user column
"""
from yoyo import step


__depends__ = {'20200706_01_qXGZz-add-user-tokens'}


upgrade_username_column = """
ALTER TABLE users
DROP COLUMN display_name,
 ADD COLUMN username VARCHAR(255) NOT NULL;
"""


downgrade_username_column = """
ALTER TABLE users
DROP COLUMN username, 
 ADD COLUMN display_name VARCHAR(255) NOT NULL;
"""


steps = [
    step(upgrade_username_column, downgrade_username_column),
]
