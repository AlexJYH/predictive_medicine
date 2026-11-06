# from functools import lru_cache
#
# from backend.repository.health.protocol import HealthRepository
# from backend.services.health.service.health import HealthService
#
#
# @lru_cache(maxsize=1)
# def get_health_service() -> HealthService:
#     return HealthService(
#         repository=HealthRepository(),
#         session_factory=,
#     )
#
#
#
#
#
#
#
#
#
#
#
#
# # @lru_cache(maxsize=1)
# # def get_plan_extension_service() -> PlanExtensionService:
# #     factory = get_async_session_factory()
# #     return PlanExtensionService(
# #         repository=PostgresPlanExtensionRepository(factory),
# #         session_factory=factory,
# #     )
#
