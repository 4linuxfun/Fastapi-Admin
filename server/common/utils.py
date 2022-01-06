import os


def menu_convert(menu_list, mode=None):
    """
    菜单转换函数，转换成嵌套的数据格式
    :param menu_list:
    :param mode: 模式，适配两种，all：对应获取详细的btn信息，None：对应生成权限菜单时使用,role:对应用户角色列表请求生成列表
    :return:
    """
    user_menus = []
    # 生成btn字典，用于后面的组合
    btn_dict = {}
    for menu in menu_list:
        if menu.type == "button":
            parent_id = menu.parent_id
            if parent_id not in btn_dict.keys():
                btn_dict[parent_id] = []
            btn_dict[parent_id].append(menu.dict())
    print(btn_dict)
    # add children
    for index, menu in enumerate(menu_list):
        if menu.parent_id is None:
            tmp = menu.dict()
            tmp['children'] = []
            # user_menus.append(tmp)
            for sub_menu in menu_list:
                if menu.id == sub_menu.parent_id:
                    if "children" not in tmp.keys():
                        tmp['children'] = []
                    info = sub_menu.dict()
                    if info['id'] in btn_dict.keys():
                        if mode is None:
                            info['meta'] = {}
                            for btn in btn_dict[info['id']]:
                                info['meta'][btn['path']] = True
                        elif mode == 'all':
                            info['children'] = []
                            for btn in btn_dict[info['id']]:
                                info['children'].append(btn)
                    tmp['children'].append(info)
            user_menus.append(tmp)
    print(user_menus)
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


def remove_tmp_file(file):
    print(f'删除临时文件{file}')
    os.remove(file)
