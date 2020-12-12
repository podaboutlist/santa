from pony import orm
from pony.orm.core import EntityMeta

db = orm.Database()


# A better way to do this would be to add get_or_create to orm.core.EntityMeta
# itself
@orm.db_session
def get_or_create(entity: EntityMeta, **kwargs) -> EntityMeta:
    """Get an Entity from the database, or create an entry if none exists.

    Args:
        entity (EntityMeta): Any class which derives from orm.Entity
        kwargs: Entity data, passed to the parent class.

    Returns:
        EntityMeta: A fetched or created instance of the Entity.
    """
    return entity.get(**kwargs) or entity(**kwargs)


db.get_or_create = get_or_create
