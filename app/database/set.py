from typing import Union, Optional

from app.database.connection import (
    Database,
    Users,
    Events,
    Admins,
    Actions,
    Data,
)
from app.logger.logger import Logger

db = Database()
logger = Logger()


def set_user(
    tg_uname: Union[str, Users.tg_uname],
    tg_id: Union[int, Users.tg_id],
) -> Users:
    with db.context_cursor() as cursor:
        user = Users(
            tg_uname=tg_uname,
            tg_id=tg_id,
        )
        cursor.add(user)
        cursor.flush()
        cursor.refresh(user)
        return user


def set_admin(
    user_id: Union[int, Admins.user_id, Users.id],
    create_uid: Union[int, Admins.create_uid, Users.id],
    active: Union[bool, Admins.active] = True,
) -> Admins:
    with db.context_cursor() as cursor:
        admin = Admins(
            user_id=user_id,
            create_uid=create_uid,
            active=active,
        )
        cursor.add(admin)
        cursor.flush()
        cursor.refresh(admin)
        return admin


def set_event(
    name: Union[str, Events.name],
    create_uid: Union[int, Events.create_uid, Users.id],
    active: Union[bool, Events.active] = True,
) -> Events:
    with db.context_cursor() as cursor:
        event = Events(
            name=name,
            create_uid=create_uid,
            active=active,
        )
        cursor.add(event)
        cursor.flush()
        cursor.refresh(event)
        return event


def set_action(
    name: Union[str, Actions.name],
    event_id: Union[int, Actions.event_id, Events.id],
    create_uid: Union[int, Actions.create_uid, Users.id],
    active: Union[bool, Actions.active] = True,
) -> Actions:
    with db.context_cursor() as cursor:
        action = Actions(
            name=name,
            event_id=event_id,
            create_uid=create_uid,
            active=active,
        )
        cursor.add(action)
        cursor.flush()
        cursor.refresh(action)
        return action


def set_data(
    action_id: Union[int, Data.action_id, Actions.id],
    create_uid: Union[int, Data.create_uid, Users.id],
    type: Union[str, Data.type],
    value: Union[str, Data.value],
    system: Optional[Union[bool, Data.system]] = False,
    active: Optional[Union[bool, Data.active]] = True,
) -> Data:
    with db.context_cursor() as cursor:
        data = Data(
            action_id=action_id,
            create_uid=create_uid,
            system=system,
            type=type,
            value=value,
            active=active,
        )
        cursor.add(data)
        cursor.flush()
        cursor.refresh(data)
        return data
