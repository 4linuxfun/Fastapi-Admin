def menu_convert(menu_list):
    """
    菜单转换函数，转换成嵌套的数据格式
    :param menu_list:
    :return:
    """
    user_menus = []
    # add children
    for index, menu in enumerate(menu_list):
        if menu.parent_id is None:
            tmp = menu.dict(exclude={"parent_id": True, "type": True})
            tmp['children'] = []
            # user_menus.append(tmp)
            for sub_menu in menu_list:
                if menu.id == sub_menu.parent_id:
                    if "children" not in tmp.keys():
                        tmp['children'] = []
                    tmp['children'].append(sub_menu.dict())
            user_menus.append(tmp)
    return user_menus


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
