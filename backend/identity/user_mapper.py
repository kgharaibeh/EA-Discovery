class UserMapper:
    def correlate(self, ldap_users: list[dict], access_entries: list[dict], asset_id: str) -> list[dict]:
        ldap_by_username = {u["username"].lower(): u for u in ldap_users if u.get("username")}

        user_access: dict[str, dict] = {}
        for entry in access_entries:
            username = entry.get("user", "").lower()
            if not username or username == "-":
                continue

            if username not in user_access:
                ldap_info = ldap_by_username.get(username, {})
                user_access[username] = {
                    "username": username,
                    "full_name": ldap_info.get("cn", ""),
                    "email": ldap_info.get("email", ""),
                    "department": ldap_info.get("department", ""),
                    "groups": ldap_info.get("groups", []),
                    "asset_id": asset_id,
                    "access_count": 0,
                    "source": "ldap+logs" if ldap_info else "logs",
                }

            user_access[username]["access_count"] += 1

        return list(user_access.values())
