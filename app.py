from common.app_factory import create_app
from common.config import settings


app = create_app(testing=settings.TESTING)


