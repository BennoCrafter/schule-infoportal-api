import hashlib
import logging
from collections import deque
from datetime import datetime
from os import stat
from typing import Optional

from src.models.last_update_model import LastUpdated
from src.substitution_manager import SubstitutionManager

logger = logging.getLogger(__name__)


class SubstitutionUpdater:
    def __init__(self):
        self.substitution_managers: deque[SubstitutionManager] = deque(maxlen=10)

    def get_substitution_manager(
        self, login_username: str, password: str
    ) -> Optional[SubstitutionManager]:
        # check if it should return demo substitution manager
        if login_username == "demo" and password == "demo":
            return SubstitutionManager(
                login_username,
                password,
                SubstitutionManager.generate_random_demo_substitutions(5),
                SubstitutionManager.generate_random_demo_news_messages(5),
            )

        hashed_login = self.hash_login(login_username, password)

        for manager in self.substitution_managers:
            if manager.authorization() == hashed_login:
                should_update = manager.check_updating_data()
                if should_update:
                    manager.update_data(login_username, password)

                return manager

        return self.create_substitution_manager(login_username, password)

    def create_substitution_manager(
        self, login_username: str, password: str
    ) -> Optional[SubstitutionManager]:
        manager = SubstitutionManager.init(
            login_username,
            password,
        )
        if manager is None:
            return None

        self.substitution_managers.append(manager)
        return manager

    @staticmethod
    def hash_login(login_username: str, password: str) -> str:
        return hashlib.sha256(f"{login_username}:{password}".encode()).hexdigest()
