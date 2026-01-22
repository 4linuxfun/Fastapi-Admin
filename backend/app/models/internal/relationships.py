from sqlmodel import SQLModel, Field, Unicode


# 这些是权限验证的基础表，单独放置
class RoleMenu(SQLModel, table=True):
    __tablename__ = "role_menu"
    role_id: int = Field(foreign_key="roles.id", primary_key=True)
    menu_id: int = Field(foreign_key="menu.id", primary_key=True)


class UserRole(SQLModel, table=True):
    __tablename__ = 'user_roles'

    user_id: int = Field(foreign_key="user.id", primary_key=True)
    role_id: int = Field(foreign_key="roles.id", primary_key=True)


# class UserJob(SQLModel, table=True):
#     """
#     通过中间表实现：用户-任务的对应关系
#     """
#     __tablename__ = 'user_job'
#     user_id: int = Field(foreign_key="user.id", primary_key=True, nullable=False)
#     job_id: str = Field(Unicode(191), foreign_key="apscheduler_jobs.id", primary_key=True, nullable=False)
