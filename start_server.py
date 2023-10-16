from logging import getLogger

import socialnetwork
from socialnetwork.core import database_manager, info

logger = getLogger(__name__)
app = socialnetwork.app

if __name__ == "__main__":
    # Prepare the database if it doesn't exist.
    if not info.Filepath.database.exists():
        logger.info("Database does not exist. Creating it now.")
        database_manager.DatabaseManager().initialize_database()

    logger.info("Starting the server.")
    app.run(host=info.Server.host, port=info.Server.port, debug=info.Server.debug)
