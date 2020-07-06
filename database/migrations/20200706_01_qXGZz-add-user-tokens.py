"""
Add user tokens
"""
from yoyo import step


__depends__ = {'20200630_01_XfukC-modify-expiration-column'}


create_user_tokens = """
CREATE TABLE user_tokens (
    id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    created_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_ts DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    token VARCHAR(255) NOT NULL UNIQUE,
    user_id BIGINT NOT NULL,
    is_active BOOL NOT NULL DEFAULT 1,
    expire_seconds INT(11) NOT NULL DEFAULT 3600,
    CONSTRAINT fk_user_token FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
)
CHARACTER SET utf8mb4;
"""


drop_user_tokens = "DROP user_tokens;"


steps = [
    step(create_user_tokens, drop_user_tokens)
]
