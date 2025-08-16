from enum import Enum


class Role(Enum):
    USER = (1, "User")
    MANAGER = (2, "Manager")
    ADMINISTRATOR = (3, "Administrator")

    def __init__(self, id, display_name):
        self.id = id
        self.display_name = display_name

    @classmethod
    def get_by_id(cls, role_id):
        return _ROLE_ID_LOOKUP.get(role_id)

    @classmethod
    def get_all(cls):
        return [(role.id, role.display_name) for role in cls]


_ROLE_ID_LOOKUP = {role.id: role for role in Role}
