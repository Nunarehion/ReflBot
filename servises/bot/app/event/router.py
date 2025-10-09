from aiogram import Router
import logging
import importlib
import pkgutil

logger = logging.getLogger(__name__)


router = Router()


core_module_name = '.core'
core_module = importlib.import_module(core_module_name, package=__name__.rsplit('.', 1)[0])

routers = []

handler_module = importlib.import_module(f"{core_module_name}.handler", package=__name__.rsplit('.', 1)[0])
for _, handler_name, _ in pkgutil.iter_modules(handler_module.__path__):
    handler_module_instance = importlib.import_module(f"{core_module_name}.handler.{handler_name}", package=__name__.rsplit('.', 1)[0])
    if hasattr(handler_module_instance, 'router'):
        routers.append(handler_module_instance.router)

callback_module = importlib.import_module(f"{core_module_name}.callback", package=__name__.rsplit('.', 1)[0])
for _, callback_name, _ in pkgutil.iter_modules(callback_module.__path__):
    callback_module_instance = importlib.import_module(f"{core_module_name}.callback.{callback_name}", package=__name__.rsplit('.', 1)[0])
    if hasattr(callback_module_instance, 'router'):
        routers.append(callback_module_instance.router)

# Подключаем FSM модули
try:
    from app.fsm.registration import router as registration_router
    routers.append(registration_router)
    logger.info("FSM registration router loaded")
except ImportError as e:
    logger.warning(f"Failed to load FSM registration router: {e}")

logger.info(f"Loaded routers: {routers}")
router.include_routers(*routers)
