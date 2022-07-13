from typing import Dict
from ...models.internal.api import ApiBase


class ApiSearch(ApiBase):
    type: Dict[str, str]
