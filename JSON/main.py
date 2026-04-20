from datetime import datetime, timezone
from pydantic import BaseModel, Field
import custom_errors
import orjson


# TODO: переименовать в User (PascalCase по PEP 8; множественное число — для коллекций).
class users(BaseModel):
    id: int
    username: str
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def load_users_from_file() -> list[dict]:
    # TODO: путь к users.json зависит от cwd — лучше pathlib от __file__ или аргумент CLI.
    # TODO: после загрузки валидировать через User.model_validate / TypeAdapter(list[User]).
    try:
        with open("users.json", "rb") as file:
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
                # TODO: не глотать ошибку — залогировать, пропустить строку или показать «некорректная дата».
                pass
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
    # TODO: не вызывать load_users_from_file() второй раз — переиспользовать all_users выше.
    all_users = load_users_from_file()
    for u in all_users:
        if u.get("id") > max_id:
            max_id = u.get("id")
    max_id += 1
    user = users(id=max_id, username=username, name=name)
    all_users.append(user.model_dump())
    with open("users.json", "wb") as file:
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
            with open("users.json", "wb") as file:
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
        # TODO: int(input()) падает на нечисловом вводе — обернуть в try/except ValueError.
        input_ = int(input())
        match input_:
            case 1:
                open_file()
            case 2:
                try:
                    write_file()
                except custom_errors.UserAlreadyExistsError as e:
                    print(e)
                    # TODO: не вызывать menu() рекурсивно — остаться в while True и continue (иначе растёт стек).
                    menu()
                except custom_errors.AddingUserError as e:
                    print(e)
                    menu()
            case 3:
                try:
                    delete_user()
                except custom_errors.UserNotFoundError as e:
                    print(e)
                    # TODO: то же — continue вместо рекурсивного menu().
                    menu()
            case 0:
                break
            case _:
                print("Неизвестный пункт меню")


if __name__ == "__main__":
    menu()
