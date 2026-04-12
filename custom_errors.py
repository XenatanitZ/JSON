from pydantic import BaseModel, ValidationError, field_validator

class UserAlreadyExistsError(Exception):
    def __init__(self, username: str):
        self.username = username
        super().__init__(f"Пользователь {username} уже существует")

class UserNotFoundError(Exception):
    def __init__(self, username: str):
        self.username = username
        super().__init__(f"Пользователь {username} не найден")

class AddingUserError(Exception):
    def __init__(self, username: str):
        self.username = username
        super().__init__(f"Ошибка при добавлении пользователя {username}")

class DeletingUserError(Exception):
    def __init__(self, username: str):
        self.username = username
        super().__init__(f"Ошибка при удалении пользователя {username}")