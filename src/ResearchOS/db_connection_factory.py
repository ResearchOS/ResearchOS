from ResearchOS.config import Config
from ResearchOS.db_connection import DBConnection, DBConnectionSQLite, DBConnectionMySQL

class DBConnectionFactory():
    """Create the appropriate DBConnection concrete class based on the database type in the config."""

    @staticmethod
    def create_db_connection() -> DBConnection:
        """Create the appropriate DBConnection concrete class based on the database type in the config."""
        # db_type = "sqlite" # For now, hard-code the database type.
        config = Config()
        db_type = config.immutable["db_type"]
        if db_type == "sqlite":
            return DBConnectionSQLite(config.db_file)
        elif db_type == "mysql":
            return DBConnectionMySQL(config.db_host, config.db_user, config.db_password, config.db_name)
        else:
            raise ValueError(f"Database type {db_type} not supported.")