import os
import websockets
from collections import defaultdict
from fastapi import WebSocket
from typing import List, Dict, Generic, Type, TypeVar
from loguru import logger
from sqlmodel import SQLModel

from ..models.internal.dictonary import DictBase
from ..models.internal.menu import MenusWithChild

T = TypeVar('T', bound=SQLModel)


class Tree(Generic[T]):
    """
    用于构建树形嵌套字段，需要有parent_id字段做关联
    """

    def __init__(self, tree_list: List[T], model: Type[T]):
        self.tree_dict: Dict[int, T] = {tree.id:model(**tree.model_dump()) for tree in tree_list}
        self.children_map:Dict[int,List[T]] = defaultdict(list)
        for tree in self.tree_dict.values():
            self.children_map[tree.parent_id].append(tree)

    def get_root_node(self) -> List[T]:
        """
        获取根节点列表
        根节点定义为在树结构中没有父节点的节点。此方法通过筛选树字典中所有没有父节点的节点来获取根节点列表。
        Returns:
            List[T]: 根节点列表，列表中的每个元素都是一个根节点对象
        """
        # 筛选树字典中所有没有父节点的节点，即根节点
        return [node for node in self.tree_dict.values() if not node.parent_id]

    def get_children(self, parent_id: int) -> List[T]:
        """
        获取指定父节点的所有子节点。

        通过递归方式构建树形结构，确保每个节点的子节点列表中包含所有间接子节点。

        Args:
            parent_id (int): 父节点的ID，用于查找其子节点。

        Returns:
            List[T]: 包含直接和间接子节点的列表。
        """
        children = self.children_map.get(parent_id, [])
        for child in children:
            # 递归获取每个子节点的子节点，并将其添加到子节点的children列表中
            child.children.extend(self.get_children(child.id))
        return children

    def build(self) -> List[T]:
        """
        构建整个树形结构。

        从根节点开始，利用 `get_children` 方法递归地为每个节点添加子节点，以构建完整的树形结构。

        Returns:
            List[T]: 完整的树形结构列表，每个元素都是从根节点开始的子树。
        """
        root_tree = self.get_root_node()
        for tree in root_tree:
            # 为根节点及其每个子节点构建完整的子节点列表
            tree.children.extend(self.get_children(tree.id))
        return root_tree


def menu_convert(menu_list) -> List[MenusWithChild]:
    """
    菜单转换函数，转换成嵌套的数据格式
    Args:
        menu_list: 菜单列表
    Returns:
        List[MenusWithChild]: 转换后的嵌套菜单列表
    """
    return Tree[MenusWithChild](menu_list, MenusWithChild).build()


def update_model(old_model, new_model):
    """
    模型数据更新函数，先把新的model转换为字典，然后迭代更新

    Args:
        old_model: 旧模型对象
        new_model: 新模型对象

    Returns:
        old_model: 更新后的旧模型对象
    """
    new = new_model.dict(exclude_unset=True)
    for key, value in new.items():
        setattr(old_model, key, value)
    return old_model


def remove_tmp_file(file):
    logger.debug(f'删除临时文件{file}')
    os.remove(file)


async def get_task_logs(ws: WebSocket, redis, session, task_id: str, trigger: str):
    key_name = f'tasks:{task_id}'
    last_id = 0
    sleep_ms = 5000
    if trigger == 'date':
        job_log.get(session,)
    while True:
        if await redis.exists(key_name):
            resp = await redis.xread({f'{key_name}': last_id}, count=1, block=sleep_ms)
            if resp:
                key, message = resp[0]
                last_id = message[0][0]
                # last_id, data = message[0]
                # data_dict = {k.decode("utf-8"): data[k].decode("utf-8") for k in data}
                try:
                    await ws.send_json({'task_id': task_id, 'data': message})
                except websockets.exceptions.ConnectionClosed as e:
                    logger.warning(f"websocket 异常关闭:{e}")
                    break
        elif last_id == 0 and (result.state == 'FAILURE' or result.state == 'SUCCESS'):
            # last_id为0表示redis中不存在key，task_id为已执行完成的任务，且redis缓存已过期
            logger.debug(f'{task_id} state:{result.state}')
            try:
                await ws.send_json({'task_id': task_id, 'data': AsyncResult(task_id).result})
            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"websocket 异常关闭:{e}")
            break
        elif result.state == 'PENDING' or result.state == 'STARTED':
            logger.debug(f"{task_id} state:{result.state}")
            continue
        else:
            logger.debug(f'{task_id}已结束')
            break
    return True
