from typing import Union, Optional

from app.database.connection import (
    Database,
    Users,
    Events,
    Admins,
    Actions,
    Data,
    insert
)
from app.logger.logger import Logger

db = Database()
logger = Logger()


def set_user(
    tg_uname: Union[str, Users.tg_uname],
    tg_id: Union[int, Users.tg_id],
) -> Users:
    no_data = True
    with db.context_cursor() as cursor:
        stmt = insert(Users)
        if isinstance(tg_uname, str):
            stmt = stmt.values(tg_uname=tg_uname)
            no_data = False
        if isinstance(tg_id, int):
            stmt = stmt.values(tg_id=tg_id)
            no_data = False
        if no_data:
            logger.warn(f"No data given for setting {Users} data.")
            return

        cursor.execute(stmt)


def set_admin(
    user_id: Union[int, Admins.user_id, Users.id],
    create_uid: Union[int, Admins.create_uid, Users.id],
    active: Union[bool, Admins.active] = True,
) -> Admins:
    no_data = True
    with db.context_cursor() as cursor:
        stmt = insert(Admins)
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
            logger.warn(f"No data given for setting {Admins} data.")
            return

        cursor.execute(stmt)


def set_event(
    name: Union[str, Events.name],
    create_uid: Union[int, Events.create_uid, Users.id],
    active: Union[bool, Events.active] = True,
) -> Events:
    no_data = True
    with db.context_cursor() as cursor:
        stmt = insert(Events)
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
            logger.warn(f"No data given for setting {Events} data.")
            return

        cursor.execute(stmt)


def set_action(
    name: Union[str, Actions.name],
    event_id: Union[int, Actions.event_id, Events.id],
    create_uid: Union[int, Actions.create_uid, Users.id],
    active: Union[bool, Actions.active] = True,
) -> Actions:
    no_data = True
    with db.context_cursor() as cursor:
        stmt = insert(Actions)
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
            logger.warn(f"No data given for setting {Actions} data.")
            return

        cursor.execute(stmt)


def set_data(
    action_id: Union[int, Data.action_id, Actions.id],
    create_uid: Union[int, Data.create_uid, Users.id],
    type: Union[str, Data.type],
    value: Union[str, Data.value],
    system: Optional[Union[bool, Data.system]] = False,
    active: Optional[Union[bool, Data.active]] = True,
) -> Data:
    no_data = True
    with db.context_cursor() as cursor:
        stmt = insert(Data)
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
            logger.warn(f"No data given for setting {Actions} data.")
            return

        cursor.execute(stmt)
