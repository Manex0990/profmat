import flask

from . import db_session
from .user import User

blueprint = flask.Blueprint(
    'news_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/news')
def get_news():
    return "Обработчик в news_api"