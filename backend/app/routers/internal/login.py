from typing import List
from loguru import logger
from fastapi import APIRouter, Depends, Request, status
from ...common.database import get_session
from sqlmodel import Session, select
from sqlalchemy.exc import NoResultFound
from ...common.response_code import ApiResponse
from ...common.security import create_access_token
from ...models.internal import User, Menu
from ...common.dep import get_uid
from ...models.internal.user import UserLogin, LoginResponse
from ... import crud
from ...common.utils import menu_convert
from ...common.captcha import CaptchaTool

router = APIRouter(prefix="/api")


@router.get("/captcha", summary="获取验证码")
async def get_captcha():
    """
    获取图形验证码
    """
    image, key = CaptchaTool.generate()
    return ApiResponse(data={"image_base64": image, "captcha_key": key})


@router.post("/login", summary="登录验证", response_model=ApiResponse[LoginResponse])
async def login(login_form: UserLogin, session: Session = Depends(get_session)):
    """
    处理登录请求，返回{token:xxxxx}，判断用户密码是否正确
    :param login_form:
    :param session
    :return:
    """
    # 验证验证码
    if not CaptchaTool.verify(login_form.captcha_key, login_form.captcha_code):
        return ApiResponse(
            code=status.HTTP_400_BAD_REQUEST,
            message="验证码错误或已失效",
        )

    try:
        user = crud.internal.user.login(session, login_form)
    except NoResultFound:
        return ApiResponse(
            code=status.HTTP_400_BAD_REQUEST,
            message="用户名或密码错误",
        )
    user_roles = []
    for role in user.roles:
        if role.enable == 1:
            user_roles.append(role.id)
    # 把roles封装再token里，每次只需要depends检查对应的roles是否有权限即可
    access_token = create_access_token(data={"uid": user.id})
    return ApiResponse(data={"uid": user.id, "token": access_token})


@router.post("/refresh", summary="刷新token")
async def refresh_token(request: Request, session: Session = Depends(get_session)):
    """
    刷新token，验证当前token有效性并生成新token
    :param request:
    :param session:
    :return:
    """
    from fastapi import HTTPException

    try:
        # 验证当前token
        uid = request.state.uid

        # 验证用户是否存在且有效
        user = session.get(User, uid)
        if not user or user.enable != 1:
            return ApiResponse(
                code=status.HTTP_401_UNAUTHORIZED, message="用户不存在或已被禁用"
            )

        # 生成新token
        new_token = create_access_token(data={"uid": uid})

        return ApiResponse(data={"token": new_token})
    except HTTPException as e:
        # 处理HTTP异常（如token过期）
        logger.error(f"Token refresh HTTP error: {e.detail}")
        return ApiResponse(code=e.status_code, message=e.detail)
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return ApiResponse(code=status.HTTP_401_UNAUTHORIZED, message="Token刷新失败")


@router.get("/permission", summary="获取权限")
async def get_permission(
    uid: int = Depends(get_uid), session: Session = Depends(get_session)
):
    """
    用户权限请求，返回拥有权限的菜单列表，前端根据返回的菜单列表信息，合成菜单项
    :param request:
    :param session:
    :param token:
    :return:
    """
    logger.debug(f"uid is:{uid}")
    user: User = crud.internal.user.get(session, uid)
    logger.debug(user.roles)
    user_menus = []
    # admin组用户获取所有菜单列表
    if uid == 1 or crud.internal.role.check_admin(session, uid):
        menu_list = session.exec(
            select(Menu).where(Menu.type != "btn", Menu.enable == 1).order_by(Menu.sort)
        ).all()
        btn_list = session.exec(
            select(Menu.auth)
            .where(Menu.type == "btn", Menu.enable == 1)
            .where(Menu.auth.is_not(None))
        ).all()
    else:
        for role in user.roles:
            user_menus.extend([menu.id for menu in role.menus])
        menu_list = session.exec(
            select(Menu)
            .where(Menu.id.in_(set(user_menus)))
            .where(Menu.type != "btn")
            .where(Menu.enable == 1)
            .order_by(Menu.sort)
        ).all()
        btn_list = session.exec(
            select(Menu.auth)
            .where(Menu.id.in_(set(user_menus)))
            .where(Menu.type == "btn")
            .where(Menu.enable == 1)
        ).all()
    user_menus = menu_convert(menu_list)

    logger.debug(f"user menus:{user_menus}")
    return ApiResponse(data={"menus": user_menus, "btns": btn_list})
