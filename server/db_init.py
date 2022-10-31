from sqlmodel import Session
from .db import init_db, engine
from .models.role import Role
from .models.user import User


def main():
    init_db()
    with Session(engine) as session:
        admin_role = Role(name='admin', description='Admin管理员组', enable=1)
        admin = User(name='admin', enable=1, password='1111111')
        admin.roles.append(admin_role)
        session.add(admin)
        session.commit()


if __name__ == '__main__':
    main()
