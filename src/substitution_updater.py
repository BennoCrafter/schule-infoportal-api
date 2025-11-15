import hashlib
from collections import deque
from datetime import datetime
from typing import Optional

from src.models.config_model import Config
from src.models.last_update_model import LastUpdated
from src.substitution_manager import SubstitutionManager
from src.utils.setup_logger import setup_logger

logger = setup_logger(__name__)


class SubstitutionUpdater:
    def __init__(self):
        self.substitution_managers: deque[SubstitutionManager] = deque(maxlen=10)

    def get_substitution_manager(
        self, config: Config, login_username: str, password: str
    ) -> Optional[SubstitutionManager]:
        # check if should return exmaple substitution manager
        if login_username == "example" and password == "example":
            return SubstitutionManager(
                login_username,
                SubstitutionManager.generate_random_example_substitutions(5),
                SubstitutionManager.generate_random_news_messages(5),
            )

        login = f"{login_username}:{password}"
        hashed_login = hashlib.sha256(login.encode()).hexdigest()

        for manager in self.substitution_managers:
            if manager.authorization == hashed_login:
                should_update = manager.check_updating_data()
                if should_update:
                    logger.info(f"Updating data for user {login_username}")
                    manager.update_data(config, login_username, password, hashed_login)

                return manager

        return self.create_substitution_manager(
            config, login_username, password, hashed_login
        )

    def create_substitution_manager(
        self, config: Config, login_username: str, password: str, authorization: str
    ) -> Optional[SubstitutionManager]:
        manager = SubstitutionManager.init(
            config,
            login_username,
            password,
            authorization=hashlib.sha256(
                f"{login_username}:{password}".encode()
            ).hexdigest(),
        )
        if manager is None:
            return None

        self.substitution_managers.append(manager)
        return manager
