import json
import os
import datetime
import websockets
import aiofiles
from collections import defaultdict
from fastapi import WebSocket
from starlette.datastructures import UploadFile
from typing import List, Dict, Generic, Type, TypeVar
from loguru import logger
from sqlmodel import SQLModel, select, Session
from app import crud

from ..models.internal.dictonary import DictBase
from ..models.internal.menu import MenusWithChild
from ..crud.base import CRUDCategory

T = TypeVar("T", bound=SQLModel)


class Tree(Generic[T]):
    """
    用于构建树形嵌套字段，需要有parent_id字段做关联
    """

    def __init__(self, tree_list: List[T], model: Type[T]):
        self.tree_dict: Dict[int, T] = {
            tree.id: model(**tree.model_dump()) for tree in tree_list
        }
        self.children_map: Dict[int, List[T]] = defaultdict(list)
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
    logger.debug(f"删除临时文件{file}")
    os.remove(file)


async def get_task_logs(ws: WebSocket, redis, session, job_id: str):
    """
    通过websocket给前端展示实时日志信息
    Args:
        ws(WebSocket): ws连接，用于给前端传递日志
        redis(Redis): redis连接，用于获取实时日志
        session(Session): 数据库连接，用于直接获取日志
        job_id(str): 任务ID
    Returns:
        None
    """
    key_name = f"tasks:{job_id}"
    last_id = 0
    sleep_ms = 5000
    while True:
        if await redis.exists(key_name):
            # key存在于redis中，从redis中实时获取日志信息
            resp = await redis.xread({f"{key_name}": last_id}, count=1, block=sleep_ms)
            if resp:
                key, message = resp[0]
                last_id = message[0][0]
                # last_id, data = message[0]
                # data_dict = {k.decode("utf-8"): data[k].decode("utf-8") for k in data}
                msg = message[0][1].get(b"msg", b"").decode("utf-8")
                try:
                    logger.debug(msg)
                    await ws.send_text(msg + "\r\n")
                except websockets.exceptions.ConnectionClosed as e:
                    logger.warning(f"websocket 异常关闭:{e}")
                    break
        else:
            # Redis 中不存在 key，从数据库的 job_logs 表中获取日志
            logger.debug(f"{job_id} 已结束，尝试从数据库获取日志")
            try:
                logs = crud.internal.job_logs.get_by_job_id(session, job_id)

                if logs:
                    await ws.send_text(json.dump(logs.log) + "\r\n")
                    logger.debug(f"从数据库获取日志成功: {len(logs)} 条记录")
                else:
                    logger.debug(f"数据库中没有 {job_id} 的日志记录")

                break  # 数据库日志获取完成后退出循环
            except Exception as e:
                logger.error(f"从数据库获取日志失败: {e}")
                return False
    return True


def generate_category_code(
    parent_id: int, db: Session, crud_instance: CRUDCategory, code_attr: str = "code"
) -> str:
    """
    生成分类编码，格式为 A01 / A01A01 / A01A01A01，字母与数字同时递增。
    Args:
        parent_id (int): 父分类ID，用于确定字母部分。
        db (Session): 数据库会话对象，用于查询已有分类。
        crud_instance (CRUDCategory): 对应的CRUD实例，需实现 get_last_category 和 get_last_subcategory 方法
        code_attr (str, optional): 模型中用于存储分类编码的属性名称。默认为 "code"。
    Returns:
        str: 生成的分类编码。
    """
    # 处理顶级分类
    if parent_id == 0:
        # 查询已有顶级分类，找到最大编号
        last_category = crud_instance.get_last_category(db)

        # 计算字母部分和数字部分
        if last_category:
            # 获取当前分类的字母和数字部分
            last_code = getattr(last_category, code_attr)
            last_letter = last_code[0]  # 字母部分
            last_number = int(last_code[1:])  # 数字部分

            # 如果数字已经到99，字母就递增
            if last_number == 99:
                new_letter = chr(ord(last_letter) + 1)  # 字母递增
                new_code = f"{new_letter}01"
            else:
                new_code = f"{last_letter}{str(last_number + 1).zfill(2)}"
        else:
            new_code = "A01"
    else:
        # 处理子分类，继承父分类字母部分
        parent_category = crud_instance.get(db, parent_id)
        if not parent_category:
            raise ValueError("父级分类不存在")

        parent_code = getattr(parent_category, code_attr)
        # 获取当前父级分类下的最大子分类编号
        last_subcategory = crud_instance.get_last_subcategory(db, parent_id)

        if last_subcategory:
            last_sub_code = getattr(last_subcategory, code_attr)
            last_sub_letter = last_sub_code[-3]
            last_sub_number = int(last_sub_code[-2:]) + 1
            # 计算新的字母部分和数字部分
            if last_sub_number > 99:
                # 如果数字部分超过99，字母部分递增，数字部分重置为01
                new_letter = chr(ord(last_sub_letter) + 1)  # 字母递增
                new_sub_code = f"{new_letter}01"
            else:
                new_sub_code = f"{last_sub_letter}{str(last_sub_number).zfill(2)}"
        else:
            new_sub_code = "A01"
        new_code = f"{parent_code}{new_sub_code}"
    return new_code


def build_hierarchical_path(
    session: Session,
    node_id: int,
    crud_instance,
    name_attr: str = "name",
    separator: str = "/",
) -> str:
    """
    构建层级结构的完整路径
    适用于任何具有parent_id字段的层级结构（如位置、分类等）

    Args:
        session (Session): 数据库会话
        node_id (int): 节点ID
        crud_instance: CRUD实例，需要有get方法
        name_attr (str): 节点名称属性，默认为"name"
        separator (str): 路径分隔符，默认为"/"

    Returns:
        str: 完整的层级路径，例如："东楼/二楼/MIS机房"

    Example:
        # 构建位置路径
        location_path = build_hierarchical_path(session, location_id, crud.assets_location)

        # 构建分类路径
        category_path = build_hierarchical_path(session, category_id, crud.assets_category)

        # 使用自定义分隔符
        path = build_hierarchical_path(session, node_id, crud_instance, separator=" > ")
    """
    if not node_id:
        return ""

    # 获取当前节点
    node = crud_instance.get(session, node_id)
    if not node:
        return ""

    # 构建路径数组
    path_parts = [getattr(node, name_attr)]
    parent_id = getattr(node, "parent_id", None)

    # 递归获取所有父级节点
    while parent_id and parent_id != 0:
        parent_node = crud_instance.get(session, parent_id)
        if not parent_node:
            break
        path_parts.insert(0, getattr(parent_node, name_attr))
        parent_id = getattr(parent_node, "parent_id", None)

    # 拼接完整路径
    return separator.join(path_parts)


def find_node_by_path(
    session: Session,
    path: str,
    crud_instance,
    name_attr: str = "name",
    separator: str = "/",
) -> int:
    """
    根据路径查找节点ID
    适用于任何具有parent_id字段的层级结构

    Args:
        session (Session): 数据库会话
        path (str): 层级路径，例如："东楼/二楼/MIS机房"
        crud_instance: CRUD实例，需要有查询方法
        name_attr (str): 节点名称属性，默认为"name"
        separator (str): 路径分隔符，默认为"/"

    Returns:
        int: 节点ID，如果未找到返回None

    Example:
        # 根据位置路径查找位置ID
        location_id = find_node_by_path(session, "东楼/二楼/MIS机房", crud.assets_location)

        # 根据分类路径查找分类ID
        category_id = find_node_by_path(session, "IT设备/服务器", crud.assets_category)
    """
    if not path or path.strip() == "":
        return None

    path_parts = [part.strip() for part in path.split(separator) if part.strip()]
    if not path_parts:
        return None

    # 从根级别开始查找
    current_parent_id = 0

    for part in path_parts:
        # 查找当前层级下的节点
        # 这里需要根据具体的CRUD实例来调整查询方法
        # 假设CRUD实例有find_by_name_and_parent方法
        node = None
        if hasattr(crud_instance, "find_by_name_and_parent"):
            node = crud_instance.find_by_name_and_parent(
                session, part, current_parent_id
            )
        else:
            # 如果没有专门的方法，使用通用查询
            from sqlmodel import select

            model_class = crud_instance.model
            stmt = select(model_class).where(
                getattr(model_class, name_attr) == part,
                getattr(model_class, "parent_id") == current_parent_id,
            )
            node = session.exec(stmt).first()

        if not node:
            return None

        current_parent_id = node.id

    return current_parent_id


async def upload_files(
    files: List[UploadFile], upload_dir: str, tag: str = "common"
) -> List[str]:
    """
    上传文件并返回文件路径列表
    :param files: 上传的文件列表
    :param upload_dir: 文件上传目录
    :param tag: 文件分类标签，如 'avatar'
    :return: 文件路径列表
    """
    image_paths = []
    if files is None or len(files) == 0:
        return image_paths

    # Determined sub-paths based on tag
    if tag == "avatar":
        # Avatars go directly into /avatar/
        relative_path = tag
    else:
        # Others go into /tag/YYYY-MM/
        current_time = datetime.datetime.now()
        date_dir = current_time.strftime("%Y-%m")
        relative_path = os.path.join(tag, date_dir)

    upload_path = os.path.join(upload_dir, relative_path)
    static_base = "/static/upload"
    static_path = os.path.join(static_base, relative_path).replace(
        "\\", "/"
    )  # Ensure web-friendly paths

    if not os.path.exists(upload_path):
        os.makedirs(upload_path)

    for file in files:
        current_time = datetime.datetime.now()
        original_filename, file_extension = os.path.splitext(file.filename)
        new_filename = f"{original_filename}_{current_time.strftime('%Y%m%d%H%M%S')}{file_extension}"
        file_path = os.path.join(upload_path, new_filename)
        # static_file_path is the URL path served by Nginx/FastAPI
        static_file_path = f"{static_path}/{new_filename}".replace("//", "/")

        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        image_paths.append(static_file_path)

    return image_paths
