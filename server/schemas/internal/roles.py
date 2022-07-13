from typing import Dict
from ...models.internal.role import RoleBase


class RoleSearch(RoleBase):
    type: Dict[str, str]