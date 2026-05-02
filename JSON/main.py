from datetime import datetime, timezone
from pydantic import BaseModel, Field
import custom_errors
import orjson
import pathlib
import logging

logger = logging.getLogger(__name__)


class User(BaseModel):
    id: int
    username: str
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def load_users_from_file() -> list[dict]:
    # TODO: после загрузки валидировать через User.model_validate / TypeAdapter(list[User]).
    try:
        with open(pathlib.Path(__file__).parent / "users.json", "rb") as file:
            raw = file.read().strip()
    except FileNotFoundError:
        return []
    if not raw:
        return []
    data = orjson.loads(raw)
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    return []


def open_file():
    data = load_users_from_file()
    for u in data:
        created_at = u.get("created_at")
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
            except ValueError:
                raise custom_errors.InvalidDateError(created_at)
        if isinstance(created_at, datetime):
            created_at = created_at.strftime("%d/%m/%Y %H:%M:%S")
        print(u.get("username"), u.get("name"), created_at)


def write_file():
    check = False
    print("Введите никнейм пользователя:")
    username = input()
    all_users = load_users_from_file()
    for u in all_users:
        if u.get("username") == username:
            raise custom_errors.UserAlreadyExistsError(username)
    print("Введите имя пользователя:")
    name = input()
    max_id = 0
    for u in all_users:
        if u.get("id") > max_id:
            max_id = u.get("id")
    max_id += 1
    user = User(id=max_id, username=username, name=name)
    all_users.append(user.model_dump())
    with open(pathlib.Path(__file__).parent / "users.json", "wb") as file:
        file.write(orjson.dumps(all_users))
    # TODO: проверка check после успешной записи почти всегда True — пересмотреть смысл AddingUserError
    # TODO: (например, проверять исключения при записи на диск или fsync).
    for u in all_users:
        if u.get("username") == username:
            check = True
            print("Пользователь успешно записан")
    if not check:
        raise custom_errors.AddingUserError(username)


def delete_user():
    check = False
    print("Введите никнейм пользователя:")
    username = input()
    all_users = load_users_from_file()
    for u in all_users:
        if u.get("username") == username:
            check = True
            # TODO: не удалять из списка во время итерации — list comprehension / удалить по индексу один раз.
            all_users.remove(u)
            with open(pathlib.Path(__file__).parent / "users.json", "wb") as file:
                file.write(orjson.dumps(all_users))
    for u in all_users:
        if u.get("username") == username:
            raise custom_errors.DeletingUserError(username)
    if not check:
        raise custom_errors.UserNotFoundError(username)
    print("Пользователь успешно удален")


def menu():
    while True:
        print("1. Открыть\n2. Записать\n3. Удалить\n0. Выход")
        try:
            input_ = int(input())
            match input_:
                case 1:
                    try:
                        open_file()
                    except custom_errors.InvalidDateError as e:
                        logging.error(e)
                        continue
                case 2:
                    try:
                        write_file()
                    except custom_errors.UserAlreadyExistsError as e:
                        logging.error(e)
                        continue
                    except custom_errors.AddingUserError as e:
                        logging.error(e)
                        continue
                case 3:
                    try:
                        delete_user()
                    except custom_errors.UserNotFoundError as e:
                        logging.error(e)
                        continue
                case 0:
                    break
                case _:
                    print("Неизвестный пункт меню")
        except ValueError:
            print("Некорректный ввод")


if __name__ == "__main__":
    menu()
