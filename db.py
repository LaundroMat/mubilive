from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient

from conf import settings

db_client = FaunaClient(secret=settings.fauna_db_key)


