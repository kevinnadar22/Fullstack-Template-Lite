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


run uv run init.py to automatically generate __init__.py file

have small doc under every func
