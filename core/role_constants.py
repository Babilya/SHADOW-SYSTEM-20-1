class UserRole:
    GUEST = "guest"
    MANAGER = "manager"
    LEADER = "leader"
    ADMIN = "admin"
    
    @classmethod
    def all_roles(cls) -> list:
        return [cls.GUEST, cls.MANAGER, cls.LEADER, cls.ADMIN]
    
    @classmethod
    def elevated_roles(cls) -> list:
        return [cls.LEADER, cls.ADMIN]
    
    @classmethod
    def staff_roles(cls) -> list:
        return [cls.MANAGER, cls.LEADER, cls.ADMIN]

ROLE_HIERARCHY = {
    UserRole.GUEST: 0,
    UserRole.MANAGER: 1,
    UserRole.LEADER: 2,
    UserRole.ADMIN: 3
}

ROLE_NAMES = {
    UserRole.GUEST: "Гість",
    UserRole.MANAGER: "Менеджер",
    UserRole.LEADER: "Лідер",
    UserRole.ADMIN: "👑 ROOT/ADMIN"
}

ROLE_DESCRIPTIONS = {
    UserRole.GUEST: "Перегляд тарифів та подача заявок",
    UserRole.MANAGER: "Оперативний виконавець: розсилки, OSINT, керування ботнетом",
    UserRole.LEADER: "Керування групою менеджерів, генерація ліцензійних ключів",
    UserRole.ADMIN: "Абсолютний контроль над системою"
}
