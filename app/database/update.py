from typing import Union, Optional

from app.database.connection import (
    Database,
    Users,
    Events,
    Admins,
    Actions,
    Data,
    update
)
from app.logger.logger import Logger

db = Database()
logger = Logger()


def update_user(
        where_id: Union[int, Users.id],
        tg_uname: Optional[Union[str, Users.tg_uname]] = None,
        tg_id: Optional[Union[int, Users.tg_id]] = None
):
    no_data = True
    with db.context_cursor() as cursor:
        stmt = update(Users).where(Users.id == where_id)
        if isinstance(tg_uname, str):
            stmt = stmt.values(tg_uname=tg_uname)
            no_data = False
        if isinstance(tg_id, int):
            stmt = stmt.values(tg_id=tg_id)
            no_data = False
        if no_data:
            logger.warn(f"No data given for updating {Users} data.")
            return

        cursor.execute(stmt)


def update_admin(
        where_id: Union[int, Admins.id],
        user_id: Optional[Union[int, Admins.user_id, Users.id]] = None,
        create_uid: Optional[Union[int, Admins.create_uid, Users.id]] = None,
        active: Optional[Union[bool, Admins.active]] = None,
):
    no_data = True
    with db.context_cursor() as cursor:
        stmt = update(Admins).where(Admins.id == where_id)
        if isinstance(user_id, int):
            stmt = stmt.values(user_id=user_id)
            no_data = False
        if isinstance(create_uid, int):
            stmt = stmt.values(create_uid=create_uid)
            no_data = False
        if isinstance(active, bool):
            stmt = stmt.values(active=active)
            no_data = False
        if no_data:
            logger.warn(f"No data given for updating {Admins} data.")
            return

        cursor.execute(stmt)


def update_event(
        where_id: Union[int, Events.id],
        name: Optional[Union[str, Events.name]] = None,
        create_uid: Optional[Union[int, Events.create_uid, Users.id]] = None,
        active: Optional[Union[bool, Events.active]] = None,
):
    no_data = True
    with db.context_cursor() as cursor:
        stmt = update(Events).where(Events.id == where_id)
        if isinstance(name, str):
            stmt = stmt.values(name=name)
            no_data = False
        if isinstance(create_uid, int):
            stmt = stmt.values(create_uid=create_uid)
            no_data = False
        if isinstance(active, bool):
            stmt = stmt.values(active=active)
            no_data = False
        if no_data:
            logger.warn(f"No data given for updating {Events} data.")
            return

        cursor.execute(stmt)


def update_action(
        where_id: Union[int, Actions.id],
        name: Optional[Union[str, Actions.name]] = None,
        event_id: Optional[Union[int, Actions.event_id, Events.id]] = None,
        create_uid: Optional[Union[int, Actions.create_uid, Users.id]] = None,
        active: Optional[Union[bool, Actions.active]] = None,
):
    no_data = True
    with db.context_cursor() as cursor:
        stmt = update(Actions).where(Actions.id == where_id)
        if isinstance(name, str):
            stmt = stmt.values(name=name)
            no_data = False
        if isinstance(event_id, int):
            stmt = stmt.values(event_id=event_id)
            no_data = False
        if isinstance(create_uid, int):
            stmt = stmt.values(create_uid=create_uid)
            no_data = False
        if isinstance(active, bool):
            stmt = stmt.values(active=active)
            no_data = False
        if no_data:
            logger.warn(f"No data given for updating {Actions} data.")
            return

        cursor.execute(stmt)


def update_data(
        where_id: Union[int, Data.id],
        action_id: Optional[Union[int, Data.action_id, Actions.id]] = None,
        create_uid: Optional[Union[int, Data.create_uid, Users.id]] = None,
        type: Optional[Union[str, Data.type]] = None,
        value: Optional[Union[str, Data.value]] = None,
        system: Optional[Optional[Union[bool, Data.system]]] = None,
        active: Optional[Optional[Union[bool, Data.active]]] = None,
):
    no_data = True
    with db.context_cursor() as cursor:
        stmt = update(Data).where(Data.id == where_id)
        if isinstance(action_id, int):
            stmt = stmt.values(action_id=action_id)
            no_data = False
        if isinstance(create_uid, int):
            stmt = stmt.values(create_uid=create_uid)
            no_data = False
        if isinstance(type, str):
            stmt = stmt.values(type=type)
            no_data = False
        if isinstance(value, str):
            stmt = stmt.values(value=value)
            no_data = False
        if isinstance(system, bool):
            stmt = stmt.values(system=system)
            no_data = False
        if isinstance(active, bool):
            stmt = stmt.values(active=active)
            no_data = False
        if no_data:
            logger.warn(f"No data given for updating {Data} data.")
            return

        cursor.execute(stmt)
