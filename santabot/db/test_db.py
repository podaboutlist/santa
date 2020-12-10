from pony import orm
from datetime import datetime, timedelta
from models import db


# HACK: We should use a real unit testing library with real unit tests
#       instead of rolling our own like I did here.
if __name__ == '__main__':
    print('--- Testing the Database ---')

    print('\n> Enabling SQL debugging...')
    orm.set_sql_debug(True)

    print('\n> Binding DB to SQLite instance in memory.')
    db.bind(provider='sqlite', filename=':memory:')

    print('\n> Generating DB mapping...')
    db.generate_mapping(create_tables=True)
    db.commit()

    with orm.db_session:
        # User IDs in the DB correspond to their Discord IDs
        print('\n> Generating Users...')
        u1 = db.User(id=143123353249513472)
        u2 = db.User(id=444183067678998540)
        u3 = db.User(id=293900315089174529)
        # Issue explicit commits otherwise the DB will batch commits and the
        # print() statements get out of sync.
        db.commit()

        print('\n> Generating Servers...')
        s1 = db.Server(id=142851181843185664)
        db.commit()

        print('\n> Generating Presents...')
        p1 = db.Present(name="test present 01", owner=u1)
        p2 = db.Present(name="test present 02", owner=u1, gifter=u2)
        p3 = db.Present(name="test present 03", owner=u3, gifter=u2)
        db.commit()

        print('\n> Displaying all Users')
        orm.select(u for u in db.User) \
           .order_by(db.User.id)[:] \
           .show()

        print('\n> Displaying all Presents')
        orm.select(p for p in db.Present) \
           .order_by(db.Present.id)[:] \
           .show()

        print('\n> Displaying all Servers')
        orm.select(s for s in db.Server) \
           .order_by(db.Server.id)[:] \
           .show()

        print('\n> Selecting gifts given by u2')
        orm.select(p for p in db.Present) \
           .filter(lambda present: present.gifter.id == u2.id) \
           .order_by(db.Present.id)[:] \
           .show()

        print('\n> All tests passed!')
