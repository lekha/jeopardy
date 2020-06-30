"""
Modify expiration column

I have been lazy about doing a proper migration here because the application is
not yet in a runnable state.
"""
from yoyo import step


__depends__ = {'20200628_01_cm3XQ-add-users'}


upgrade_expiration_column = """
ALTER TABLE user_metadata_anonymous
DROP COLUMN expire_ts,
 ADD COLUMN expire_seconds INT(11) NOT NULL;
"""


downgrade_expiration_column = """
ALTER TABLE user_metadata_anonymous
DROP COLUMN expire_seconds,
 ADD COLUMN expire_ts DATETIME(6) NOT NULL;
"""


steps = [
    step(upgrade_expiration_column, downgrade_expiration_column),
]
