import os
from typing import List
from ..models.internal.menu import MenusWithChild


class MenuTree:
    def __init__(self, menu_list):
        self.menu_list = []
        for menu in menu_list:
            self.menu_list.append(MenusWithChild(**menu.dict()))

    def get_root_node(self):
        root_menus = []
        for menu in self.menu_list:
            if menu.type == 'page':
                root_menus.append(menu)
        return root_menus

    def get_children(self, parent_menu: MenusWithChild):
        children = []
        for menu in self.menu_list:
            if menu.parent_id == parent_menu.id:
                menu.children = self.get_children(menu)
                children.append(menu)
        return children

    def build(self):
        root_menus = self.get_root_node()
        for menu in root_menus:
            menu.children = self.get_children(menu)
        return root_menus


def menu_convert(menu_list) -> List[MenusWithChild]:
    """
    菜单转换函数，转换成嵌套的数据格式
    :param menu_list:
    :return:
    """
    return MenuTree(menu_list).build()


def update_model(old_model, new_model):
    """
    模型数据更新函数，先把新的model转换为字典，然后迭代更新
    :param old_model:
    :param new_model:
    :return:
    """
    new = new_model.dict(exclude_unset=True)
    for key, value in new.items():
        setattr(old_model, key, value)
    return old_model


def remove_tmp_file(file):
    print(f'删除临时文件{file}')
    os.remove(file)
