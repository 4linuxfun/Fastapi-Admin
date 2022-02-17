from fastapi import APIRouter, Request
from ..schemas import ApiResponse
from ..models import User

router = APIRouter(prefix='/api')


# class UserForm(User):
#     roles: List[Role]


@router.get('/form/{name}')
async def get_form_model(name: str, request: Request):
    print(name)
    print(request.app.openapi())
    print(request.app.openapi()['components']['schemas'][name]['properties'])
    return ApiResponse(
        code=0,
        message='success',
        data=User.schema_json()
    )
