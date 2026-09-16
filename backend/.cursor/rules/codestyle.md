Have third party clients under app/integrations

use utils for utility functions

use services for business logic

and repository for db calls,

never call db from handler or utils, call only from service through repository

have environ variables under app/core/config.py

raise exceptions from app/core/exceptions.py

use logger.loguru for logging

have pydantic schemas for complex data structures, for inpur or request schemas, have it under app/domain/schemas/request

example

@router.get("", response_model=schemas.APIResponse[schemas.HealthResponse])
async def health_check() -> schemas.APIResponse[schemas.HealthResponse]:
    """
    Health check endpoint for Docker and monitoring systems.

    Returns:
        APIResponse[HealthResponse]: Status of the application
    """
    return schemas.APIResponse(
        data=schemas.HealthResponse(status="healthy", service="api", version="1.0.0")
    )


always uyse repsonse_model=
and always the response has to go through APIResponse

the import should be like

from app.x import y

use it like y.z, dont do like: from app.w.x.y import z

this is wrong: from app.domain.schemas.response.product import ProductListResponse
this is right: from app.domain import schemas, schemas.ProductListResponse

log every detail with info, debug, warning, error using loguru like
logger.bind(arg=v).info(message)
you can use with logfire.span(..) for required part where we want to trace a particular external integration timing, success, failure

write unittests for handler, and utils, and service, not for repostiory, and models,
write tests only for logically required functions, not for all functions where the results is obvious

run uv run init.py to automatically generate __init__.py file

have small doc under every func


## Strict imports (extra)

Never import deeper than `app.<package>` (or a package-exported submodule). No `app.x.y.z` consumer imports.

Allowed:

```python
from app.domain import models
from app.domain import schemas
from app.service import surcharge
from app.service import CartService
from app.repository import OrderRepository
from app.utils import order_utils
```

Use as:

```python
models.SalesChannel
schemas.ProductListResponseData
surcharge.SurchargeService
```

Forbidden:

```python
from app.domain.models.enums import SalesChannel
from app.domain.schemas.response.product import ProductListResponse
from app.service.surcharge import SurchargeService
from app.repository.order import OrderRepository
from app.utils.order import OrderUtils
```

Wrong → right:

- `from app.domain.models.enums import SalesChannel` → `from app.domain import models` then `models.SalesChannel`
- `from app.service.surcharge import SurchargeService` → `from app.service import surcharge` then `surcharge.SurchargeService`
- `from app.repository.order import OrderRepository` → `from app.repository import OrderRepository`

Exception: files inside `app/domain/models/` may use relative imports (`from .enums import ...`).
