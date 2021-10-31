from typing import List, Union
from sqlmodel import Session, select
from .models import *
from ..common import utils


def get_menu_list(roles: Union[List[int], str], session: Session, enable=False) -> List[Menu]:
    """
    通过role_id，获取对应的menu清单
    :param roles:
    :param session:
    :param enable:True则过滤，只显示enable的菜单
    :return:
    """
    if isinstance(roles, str):
        if roles == 'admin':
            sql = select(Menu)
    else:
        sql = select(RoleMenu).where(RoleMenu.role_id.in_(roles))
        result = session.exec(sql)
        menu_list = [menu.menu_id for menu in result]
        sql = select(Menu).where(Menu.id.in_(menu_list))
    # 普通用户才需要过滤菜单，admin对于所有菜单都开放，不需要过滤
    if enable:
        sql = sql.where(Menu.enable == 1)
    results = session.exec(sql)
    return [menu for menu in results]


def update_menu(menu: Menu, session: Session):
    if menu.id:
        # 存在菜单id，则为更新
        sql = select(Menu).where(Menu.id == menu.id)
        result = session.exec(sql).one()
        print(result)
        # menu_data = menu.dict(exclude_unset=True)
        # for key, value in menu_data.items():
        #     setattr(result, key, value)
        result = utils.update_model(result, menu)
        session.add(result)
    else:
        session.add(menu)
    session.commit()


def get_role_menus(role_id: int, session: Session) -> List[int]:
    """
    通过role_id获取对应角色拥有权限的菜单列表
    :param role_id:
    :param session:
    :return: List[int]
    """
    sql = select(RoleMenu).where(RoleMenu.role_id == role_id)
    result = session.exec(sql)
    return [role.menu_id for role in result]


def update_role_menus(role_id: int, new_menus: List[int], session: Session):
    sql = select(Role).where(Role.id == role_id)
    role = session.exec(sql).one()
    print(role.menus)
    menus = session.exec(select(Menu).where(Menu.id.in_(new_menus))).all()
    role.menus = menus
    session.add(role)
    session.commit()


def update_role(role: Role, session: Session):
    """
    更新role表字段信息
    :param role:
    :param session:
    :return:
    """
    if role.id is not None:
        print('更新')
        sql = select(Role).where(Role.id == role.id)
        role_info = session.exec(sql).one()
        role_info = utils.update_model(role_info, role)
    else:
        role_info = role
    session.add(role_info)
    session.commit()
    session.refresh(role_info)
    return role_info.id
