from typing import Optional
import sys
from pathlib import Path


import bcrypt

root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

# --- Импорты твоих репозиториев ---
from src.repositories.user_rep import create, get_all
from src.repositories.Participant_rep import create as create_participant, get_by_rid as get_participant_by_id, participant_update, participant_delete
from src.repositories.Competition_rep import create as create_competition, get_by_rid as get_competition_by_id, competition_update, competition_delete
from src.repositories.Rankings_res import save_result, get_tournament_table

# --- Хеширование и проверка пароля ---

class AuthError(Exception):
    pass

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

def login_user(username: str, password: str) -> dict:
    users = get_all()                          # получаем всех пользователей
    user = next((u for u in users if u.username == username), None)

    if user is None:
        raise AuthError("Неверный логин или пароль.")
    if not verify_password(password, user.password_hash):
        raise AuthError("Неверный логин или пароль.")

    return {
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role 
    }

def register_new_user(username: str, password: str, role: str = "participant") -> int:
    if len(username) < 3:
        raise AuthError("Логин должен быть не короче 3 символов.")
    if len(password) < 6:
        raise AuthError("Пароль должен быть не короче 6 символов.")

    salt = bcrypt.gensalt(rounds=12)
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    return create(username, password_hash, role)

# --- Глобальная сессия ---
current_user: Optional[dict] = None

def clear():
    print("\n" * 2)

def header(title: str):
    print("=" * 40)
    print(f"  {title}")
    print("=" * 40)

# --- Сначала объявляем все функции, которые вызывает main_menu ---

def manage_participants(is_admin: bool):
    while True:
        clear()
        header("УЧАСТНИКИ")
        if is_admin:
            print("1. Добавить участника")
            print("2. Обновить участника")
            print("3. Удалить участника")
        else:
            print("1. Просмотреть участника по ID")
        print("4. Назад")
        c = input("Действие: ").strip()
        if c == "4": break

        try:
            if is_admin and c == "1":
                name = input("ФИО: ").strip()
                dob = input("Дата рождения (YYYY-MM-DD): ").strip()
                pid = create_participant(current_user["user_id"], name, dob)
                print(f"✅ Участник добавлен, ID={pid}")

            elif is_admin and c == "2":
                pid_str = input("ID участника: ").strip()
                if not pid_str.isdigit():
                    print("❌ ID должен быть числом.")
                    input("Enter...")
                    continue
                pid = int(pid_str)
                existing = get_participant_by_id(pid)
                if existing is None:
                    print("❌ Участник не найден.")
                    input("Enter...")
                    continue

                new_name = input(f"Новое ФИО (текущее: {existing.full_name}, оставьте пустым): ").strip() or None
                new_dob = input(f"Новая дата рождения (текущая: {existing.date_of_birth}, оставьте пустым): ").strip() or None
                ok = participant_update(pid, full_name=new_name, birth_date=new_dob, sport=None)
                print("✅ Обновлено" if ok else "⚠️ Не обновлено")

            elif is_admin and c == "3":
                pid_str = input("ID для удаления: ").strip()
                if not pid_str.isdigit():
                    print("❌ ID должен быть числом.")
                    input("Enter...")
                    continue
                pid = int(pid_str)
                ok = participant_delete(pid)
                print("✅ Удалено" if ok else "❌ Не найден")

            else:
                # Обычный пользователь: только просмотр
                pid_str = input("Введите ID участника для просмотра: ").strip()
                if not pid_str.isdigit():
                    print("❌ ID должен быть числом.")
                    input("Enter...")
                    continue
                pid = int(pid_str)
                p = get_participant_by_id(pid)
                if p:
                    print(f"\n👤 Участник: {p.full_name}, дата рождения: {p.date_of_birth}")
                else:
                    print("❌ Участник не найден.")

        except Exception as e:
            print(f"❌ Ошибка: {e}")
        input("Нажмите Enter для продолжения...")


def manage_competitions(is_admin: bool):
    while True:
        clear()
        header("СОРЕВНОВАНИЯ")
        if is_admin:
            print("1. Создать соревнование")
            print("2. Обновить соревнование")
            print("3. Удалить соревнование")
        else:
            print("1. Посмотреть соревнование по ID")
        print("4. Назад")
        c = input("Действие: ").strip()
        if c == "4": break

        try:
            if is_admin and c == "1":
                name = input("Название: ").strip()
                date = input("Дата (YYYY-MM-DD): ").strip()
                cid = create_competition(name, date)
                print(f"✅ Соревнование создано, ID={cid}")

            elif is_admin and c == "2":
                cid_str = input("ID соревнования: ").strip()
                if not cid_str.isdigit():
                    print("❌ ID должно быть числом.")
                    input("Enter...")
                    continue
                cid = int(cid_str)
                existing = get_competition_by_id(cid)
                if existing is None:
                    print("❌ Соревнование не найдено.")
                    input("Enter...")
                    continue

                new_name = input(f"Новое название (текущее: {existing.name}, оставьте пустым): ").strip() or None
                new_date = input(f"Новая дата (текущая: {existing.date}, оставьте пустым): ").strip() or None
                ok = competition_update(cid, name=new_name, date=new_date, sport=None)
                print("✅ Обновлено" if ok else "⚠️ Не обновлено")

            elif is_admin and c == "3":
                cid_str = input("ID для удаления: ").strip()
                if not cid_str.isdigit():
                    print("❌ ID должно быть числом.")
                    input("Enter...")
                    continue
                cid = int(cid_str)
                ok = competition_delete(cid)
                print("✅ Удалено" if ok else "❌ Не найдено")

            else:
                # Обычный пользователь: только просмотр
                cid_str = input("Введите ID соревнования для просмотра: ").strip()
                if not cid_str.isdigit():
                    print("❌ ID должно быть числом.")
                    input("Enter...")
                    continue
                cid = int(cid_str)
                c = get_competition_by_id(cid)
                if c:
                    print(f"\n🏆 Соревнование: {c.name}, дата: {c.date}")
                else:
                    print("❌ Соревнование не найдено.")

        except Exception as e:
            print(f"❌ Ошибка: {e}")
        input("Нажмите Enter для продолжения...")


def record_result(is_admin: bool):
    clear()
    header("ЗАФИКСИРОВАТЬ РЕЗУЛЬТАТ")

    if not is_admin:
        print("⚠️ У вас нет прав на фиксацию результатов. Обратитесь к администратору.")
        input("Нажмите Enter...")
        return

    try:
        pid_str = input("ID участника: ").strip()
        cid_str = input("ID соревнования: ").strip()
        score_str = input("Результат (число): ").strip()

        if not (pid_str.isdigit() and cid_str.isdigit()):
            print("❌ ID должны быть числами.")
            input("Enter...")
            return

        pid = int(pid_str)
        cid = int(cid_str)
        score = float(score_str)

        rid = save_result(pid, cid, score)
        print(f"✅ Результат сохранён, result_id={rid}")
    except ValueError:
        print("❌ Неверный формат числа.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    input("Нажмите Enter...")


def show_rankings():
    clear()
    header("ТАБЛИЦА РЕЙТИНГОВ")
    print("1. По одному соревнованию (введите ID)")
    print("2. Все соревнования")
    c = input("Выбор: ").strip()

    try:
        if c == "1":
            cid_str = input("ID соревнования: ").strip()
            if not cid_str.isdigit():
                print("❌ ID должно быть числом.")
                input("Enter...")
                return
            cid = int(cid_str)
            rows = get_tournament_table(competition_id=cid)
        else:
            rows = get_tournament_table()

        if not rows:
            print("📭 Таблица пуста.")
        else:
            print(f"{'ФИО':<25} {'Результат':>10} {'Место':>6}")
            print("-" * 45)
            for r in rows:
                fname = getattr(r, "full_name", "?")
                res = getattr(r, "result", "?")
                plc = getattr(r, "place", "?")
                print(f"{fname:<25} {str(res):>10} {str(plc):>6}")
    except Exception as e:
        print(f"❌ Ошибка при получении таблицы: {e}")

    input("Нажмите Enter для возврата...")


# --- Меню авторизации ---
def auth_menu():
    global current_user
    while current_user is None:
        clear()
        header("АВТОРИЗАЦИЯ")
        print("1. Войти")
        print("2. Зарегистрироваться")
        print("3. Выход")
        choice = input("Выберите: ").strip()

        if choice == "3":
            print("До свидания.")
            sys.exit(0)

        elif choice == "1":
            username = input("Логин: ").strip()
            password = input("Пароль: ").strip()
            try:
                current_user = login_user(username, password)
                print(f"\n✅ Вы вошли как {current_user['username']} ({current_user['role']})")
            except AuthError as e:
                print(f"\n❌ Ошибка: {e}")
                input("Нажмите Enter, чтобы продолжить...")

        elif choice == "2":
            # Авто-админ для логина 'admin'
            username = input("Придумайте логин (≥3 символов): ").strip()
            password = input("Придумайте пароль (≥6 символов): ").strip()
            if username.lower() == "admin":
                role = "judge"      
            else:
                role = "participant"
            try:
                uid = register_new_user(username, password, role)
                print(f"\n✅ Пользователь создан с ID={uid}, роль={role}. Теперь войдите.")
                input("Нажмите Enter...")
            except AuthError as e:
                print(f"\n❌ Ошибка регистрации: {e}")
                input("Нажмите Enter...")

# --- Основное меню ---
def main_menu():
    global current_user
    is_admin = current_user["role"] == "judge"

    while True:
        clear()
        header(f"ГЛАВНОЕ МЕНЮ — {current_user['username']} ({current_user['role']})")
        print("1. Участники (просмотр / управление)")
        print("2. Соревнования (просмотр / управление)")
        print("3. Зафиксировать результат")
        print("4. Таблица рейтингов")
        print("5. Выйти из аккаунта")

        if not is_admin:
            print("\n⚠️ Режим просмотра: редактирование недоступно.")

        choice = input("Выбор: ").strip()

        if choice == "5":
            current_user = None
            print("Вы вышли.")
            break

        elif choice == "1":
            manage_participants(is_admin)

        elif choice == "2":
            manage_competitions(is_admin)

        elif choice == "3":
            record_result(is_admin)

        elif choice == "4":
            show_rankings()

if __name__ == "__main__":
    print("🚀 Система управления спортивными результатами")
    auth_menu()
    while current_user is not None:
        main_menu()