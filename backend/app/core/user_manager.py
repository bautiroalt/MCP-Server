import logging
import json
import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Define the path for the user data JSON file
USERS_FILE = "data/users/users.json"

class User(BaseModel):
    """Basic User model."""
    username: str
    hashed_password: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    roles: List[str] = []
    disabled: bool = False

class UserManager:
    """Manages user data, including persistence to a JSON file."""
    def __init__(self, pwd_context: CryptContext):
        logger.info("Initializing User Manager")
        self.pwd_context = pwd_context
        self._users: Dict[str, User] = {}
        self._load_users()

    def _load_users(self):
        """Loads users from the JSON file."""
        user_data_path = USERS_FILE
        if os.path.exists(user_data_path):
            try:
                with open(user_data_path, "r") as f:
                    users_data = json.load(f)
                    for user_dict in users_data:
                        if "hashed_password" in user_dict:
                            self._users[user_dict["username"]] = User(**user_dict)
                logger.info(f"Loaded {len(self._users)} users from {USERS_FILE}")
            except Exception as e:
                logger.error(f"Error loading users from {USERS_FILE}: {e}")
        else:
            logger.info(f"{USERS_FILE} not found, starting with no users.")
            self._create_default_users()

    def _save_users(self):
        """Saves current users to the JSON file."""
        user_data_path = USERS_FILE
        try:
            os.makedirs(os.path.dirname(user_data_path), exist_ok=True)
            with open(user_data_path, "w") as f:
                json.dump([user.model_dump() for user in self._users.values()], f, indent=4)
            logger.info(f"Saved {len(self._users)} users to {USERS_FILE}")
        except Exception as e:
            logger.error(f"Error saving users to {USERS_FILE}: {e}")

    def _create_default_users(self):
        """Creates initial default users if the user file doesn't exist."""
        logger.info("Creating default users...")
        self.create_user_sync("Jatin23K", "#JK2025sy#", email="jatin@example.com", full_name="Jatin", roles=["admin"])
        self.create_user_sync("coder1", "securepass", email="coder1@example.com", full_name="Coder One", roles=["user"])
        self._save_users()

    def create_user_sync(self, username: str, password: str, email: Optional[str] = None, full_name: Optional[str] = None, roles: Optional[List[str]] = None) -> User:
        """Synchronously create a new user and hash password (for initial setup)."""
        if username in self._users:
            logger.warning(f"Attempted to create user '{username}' which already exists.")
            return self._users[username]

        hashed_password = self.pwd_context.hash(password)
        new_user = User(username=username, hashed_password=hashed_password, email=email, full_name=full_name, roles=roles or [])
        self._users[username] = new_user
        logger.info(f"User '{username}' created (sync).")
        return new_user

    async def create_user(self, username: str, password: str, email: Optional[str] = None, full_name: Optional[str] = None, roles: Optional[List[str]] = None) -> User:
        """Asynchronously create a new user, hash password, and save."""
        if username in self._users:
            raise ValueError(f"User '{username}' already exists")

        hashed_password = self.pwd_context.hash(password)
        new_user = User(username=username, hashed_password=hashed_password, email=email, full_name=full_name, roles=roles or [])
        self._users[username] = new_user
        self._save_users()
        logger.info(f"User '{username}' created.")
        return new_user

    async def get_user(self, username: str) -> Optional[User]:
        """Asynchronously get a user by username."""
        return self._users.get(username)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        return self.pwd_context.verify(plain_password, hashed_password)

# Singleton instance (initialized in main.py)
user_manager: Optional[UserManager] = None

# Dependency to get the UserManager instance
async def get_user_manager() -> UserManager:
    """Dependency for FastAPI to get the user manager instance."""
    if user_manager is None:
        logger.error("UserManager not initialized!")
        raise RuntimeError("User manager not initialized")
    return user_manager 