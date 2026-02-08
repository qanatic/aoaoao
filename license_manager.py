import json
import os
import secrets
import string
from datetime import datetime, timedelta

DEFAULT_LICENSE_DATA = {
    "licenses": ["DEMO-1234-ABCD"],
    "temporary_codes": {}
}


def resource_path(base_dir, filename):
    """Возвращает полный путь к файлу рядом с exe или py."""
    return os.path.join(base_dir, filename)


def load_json_data(path, default):
    if not os.path.exists(path):
        save_json_data(path, default)
        return default
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json_data(path, payload):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def normalize_code(code):
    return code.strip().upper()


def get_license_data(base_dir):
    path = resource_path(base_dir, "license_data.json")
    return load_json_data(path, DEFAULT_LICENSE_DATA.copy())


def save_license_data(base_dir, data):
    path = resource_path(base_dir, "license_data.json")
    save_json_data(path, data)


def get_active_code(base_dir):
    path = resource_path(base_dir, "license_config.json")
    data = load_json_data(path, {"active_code": ""})
    return normalize_code(data.get("active_code", ""))


def set_active_code(base_dir, code):
    path = resource_path(base_dir, "license_config.json")
    save_json_data(path, {"active_code": normalize_code(code)})


def cleanup_expired_codes(data):
    now = datetime.utcnow()
    temp_codes = data.get("temporary_codes", {})
    expired = [code for code, meta in temp_codes.items()
               if datetime.fromisoformat(meta["expires_at"]) <= now]
    for code in expired:
        temp_codes.pop(code, None)
    data["temporary_codes"] = temp_codes
    return data, expired


def is_code_valid(code, data):
    code = normalize_code(code)
    if not code:
        return False
    if code in data.get("licenses", []):
        return True
    temp_codes = data.get("temporary_codes", {})
    meta = temp_codes.get(code)
    if not meta:
        return False
    return datetime.fromisoformat(meta["expires_at"]) > datetime.utcnow()


def generate_temp_code(base_dir, data, hours):
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = "TEMP-" + "".join(secrets.choice(alphabet) for _ in range(8))
        if code not in data.get("temporary_codes", {}) and code not in data.get("licenses", []):
            break
    expires_at = datetime.utcnow() + timedelta(hours=hours)
    data.setdefault("temporary_codes", {})[code] = {
        "expires_at": expires_at.isoformat()
    }
    save_license_data(base_dir, data)
    return code, expires_at


def generate_license_code(base_dir, data):
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = "LIC-" + "".join(secrets.choice(alphabet) for _ in range(12))
        if code not in data.get("licenses", []) and code not in data.get("temporary_codes", {}):
            break
    data.setdefault("licenses", []).append(code)
    save_license_data(base_dir, data)
    return code


def add_license_code(base_dir, data, code):
    normalized = normalize_code(code)
    if not normalized:
        return False
    licenses = data.setdefault("licenses", [])
    if normalized in licenses:
        return False
    licenses.append(normalized)
    save_license_data(base_dir, data)
    return True


def remove_license_code(base_dir, data, code):
    normalized = normalize_code(code)
    licenses = data.get("licenses", [])
    if normalized not in licenses:
        return False
    licenses.remove(normalized)
    save_license_data(base_dir, data)
    return True