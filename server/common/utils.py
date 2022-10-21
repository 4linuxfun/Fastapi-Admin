import os
from typing import List, Generic, Type, TypeVar
from sqlmodel import SQLModel
from ..models.internal.menu import MenusWithChild

T = TypeVar('T', bound=SQLModel)


class Tree(Generic[T]):
    """
    用于构建树形嵌套字段，需要有parent_id字段做关联
    """

    def __init__(self, tree_list: List[T], model: Type[T]):
        self.tree_list = []
        for tree in tree_list:
            self.tree_list.append(model(**tree.dict()))

    def get_root_node(self):
        root_tree = []
        for tree in self.tree_list:
            if not tree.parent_id:
                root_tree.append(tree)
        return root_tree

    def get_children(self, parent_id: int) -> List[T]:
        children = []
        for tree in self.tree_list:
            if tree.parent_id == parent_id:
                tree.children.extend(self.get_children(tree.id))
                children.append(tree)
        return children

    def build(self) -> List[T]:
        root_tree = self.get_root_node()
        for tree in root_tree:
            tree.children.extend(self.get_children(tree.id))
        return root_tree


def menu_convert(menu_list) -> List[MenusWithChild]:
    """
    菜单转换函数，转换成嵌套的数据格式
    :param menu_list:
    :return:
    """
    return Tree[MenusWithChild](menu_list, MenusWithChild).build()


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
