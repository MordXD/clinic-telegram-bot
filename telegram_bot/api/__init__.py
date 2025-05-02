from .applications import router as applications_router
from .reviews import router as reviews_router
from .stats import router as stats_router
from .jwt_auth import router as auth_router

all_routers = [
    applications_router,
    reviews_router,
    stats_router,
    auth_router
] 