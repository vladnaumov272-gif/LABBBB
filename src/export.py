import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from er import get_connection # подключение из вашего модуля

OUT_DIR = Path(__file__).resolve().parent / "out"

SQL = """
SELECT p.participant_id,
       p.full_name,
       p.date_of_birth,
       c.name  AS competition_name,
       c.date  AS competition_date,
       r.result
FROM Participants p
LEFT JOIN Results r      ON p.participant_id = r.participant_id
LEFT JOIN Competitions c ON r.competition_id = c.competition_id
"""


def fetch_data() -> list[dict]:
    """Извлекает данные из БД и собирает вложенную структуру."""
    conn = get_connection()
    try:
        rows = [dict(r) for r in conn.execute(SQL)]
    finally:
        conn.close()

    participants: dict[int, dict] = {}
    for row in rows:
        pid = row["participant_id"]
        if pid not in participants:
            participants[pid] = {
                "participant_id": pid,
                "full_name": row["full_name"],
                "date_of_birth": row["date_of_birth"],
                "results": [],
            }
        if row["competition_name"] is not None:
            participants[pid]["results"].append({
                "competition_name": row["competition_name"],
                "competition_date": row["competition_date"],
                "result": row["result"],
            })
    return list(participants.values())


# ---------- JSON ----------

def export_json(data: list[dict], path: Path) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------- YAML (вручную, без pyyaml) ----------

def yaml_scalar(value) -> str:
    """Представление простого значения в YAML."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    # строки всегда в кавычках — безопасно для дат, пробелов и спецсимволов
    return json.dumps(str(value), ensure_ascii=False)


def key_lines(prefix: str, key: str, value, child_indent: int) -> list[str]:
    """Строки для одной пары ключ: значение (со вложенностью, если она есть)."""
    if isinstance(value, (dict, list)) and value:
        return [f"{prefix}{key}:"] + to_yaml(value, child_indent).split("\n")
    if isinstance(value, list) and not value:
        return [f"{prefix}{key}: []"]
    return [f"{prefix}{key}: {yaml_scalar(value)}"]


def to_yaml(data, indent: int = 0) -> str:
    """Рекурсивно превращает словари и списки в текст YAML."""
    pad = "  " * indent
    lines = []
    if isinstance(data, dict):
        for key, value in data.items():
            lines += key_lines(pad, key, value, indent + 1)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item:
                first = True
                for key, value in item.items():
                    prefix = f"{pad}- " if first else f"{pad}  "
                    lines += key_lines(prefix, key, value, indent + 2)
                    first = False
            else:
                lines.append(f"{pad}- {yaml_scalar(item)}")
    return "\n".join(lines)


def export_yaml(data: list[dict], path: Path) -> None:
    path.write_text(to_yaml(data) + "\n", encoding="utf-8")


# ---------- XML ----------

def export_xml(data: list[dict], path: Path) -> None:
    root = ET.Element("participants")
    for p in data:
        p_el = ET.SubElement(root, "participant")
        for key, value in p.items():
            if key == "results":
                res_el = ET.SubElement(p_el, "results")
                for r in value:
                    r_el = ET.SubElement(res_el, "result")
                    for rk, rv in r.items():
                        ET.SubElement(r_el, rk).text = str(rv)
            else:
                ET.SubElement(p_el, key).text = str(value)
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


# ---------- CSV ----------

def export_csv(data: list[dict], path: Path) -> None:
    """CSV не поддерживает вложенность: каждый результат — отдельная строка."""
    headers = ["participant_id", "full_name", "date_of_birth",
               "competition_name", "competition_date", "result"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(headers)
        for p in data:
            if p["results"]:
                for r in p["results"]:
                    writer.writerow([p["participant_id"], p["full_name"],
                                     p["date_of_birth"], r["competition_name"],
                                     r["competition_date"], r["result"]])
            else:
                writer.writerow([p["participant_id"], p["full_name"],
                                 p["date_of_birth"], "", "", ""])


# ---------- Запуск ----------

def main() -> None:
    conn = get_connection()
    conn.close()               # проверяем, что БД открывается; таблицы уже есть
    OUT_DIR.mkdir(exist_ok=True)
    data = fetch_data()    
    

    export_json(data, OUT_DIR / "data.json")
    export_csv(data, OUT_DIR / "data.csv")
    export_xml(data, OUT_DIR / "data.xml")
    export_yaml(data, OUT_DIR / "data.yaml")

    print(f"Экспорт завершён: {len(data)} участников, файлы в {OUT_DIR}")


if __name__ == "__main__":
    main()
