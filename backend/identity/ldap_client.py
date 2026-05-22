from ldap3 import Server, Connection, ALL, SUBTREE

from app.config import settings


class LDAPClient:
    def __init__(self):
        self._server = None
        self._conn = None

    async def connect(self) -> None:
        if not settings.ldap_url:
            raise ValueError("LDAP URL not configured")
        self._server = Server(settings.ldap_url, get_info=ALL)
        self._conn = Connection(
            self._server,
            user=settings.ldap_bind_dn,
            password=settings.ldap_bind_password,
            auto_bind=True,
        )

    async def search_users(self, search_filter: str = "(objectClass=person)") -> list[dict]:
        if not self._conn:
            await self.connect()

        self._conn.search(
            search_base=settings.ldap_base_dn,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=["cn", "sAMAccountName", "mail", "memberOf", "department"],
        )

        users = []
        for entry in self._conn.entries:
            users.append({
                "cn": str(entry.cn) if hasattr(entry, "cn") else "",
                "username": str(entry.sAMAccountName) if hasattr(entry, "sAMAccountName") else "",
                "email": str(entry.mail) if hasattr(entry, "mail") else "",
                "department": str(entry.department) if hasattr(entry, "department") else "",
                "groups": [str(g) for g in entry.memberOf] if hasattr(entry, "memberOf") else [],
            })
        return users

    async def get_groups(self) -> list[dict]:
        if not self._conn:
            await self.connect()

        self._conn.search(
            search_base=settings.ldap_base_dn,
            search_filter="(objectClass=group)",
            search_scope=SUBTREE,
            attributes=["cn", "member"],
        )

        groups = []
        for entry in self._conn.entries:
            groups.append({
                "name": str(entry.cn) if hasattr(entry, "cn") else "",
                "members": [str(m) for m in entry.member] if hasattr(entry, "member") else [],
            })
        return groups

    async def disconnect(self) -> None:
        if self._conn:
            self._conn.unbind()
            self._conn = None
