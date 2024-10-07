from datetime import datetime
from typing import List, Tuple, Union

from app.database.connection import (
    Database,
    select,
    Users,
    Admins,
    Events,
    Actions,
    Data,
    cast_data,
)
from app.logger.logger import Logger

db = Database()
logger = Logger()


# def get_type(
#         id: Union[
#             int,
#             None,
#         ] = None,
#         system: Union[
#             bool,
#             None,
#         ] = None,
#         value: Union[
#             str,
#             None,
#         ] = None,
# ) -> Union[Types, None]:
#     no_data = True
#     with db.context_cursor() as cursor:
#         stmt = select(Types)
#         if isinstance(id, int):
#             stmt = stmt.where(Types.id == id)
#             no_data = False
#         if isinstance(system, bool):
#             stmt = stmt.where(Types.system == system)
#             no_data = False
#         if isinstance(value, str):
#             stmt = stmt.where(Types.value == value)
#             no_data = False
#         if no_data:
#             logger.warn(f"No data given for fetching {Types} data. Return None.")
#             stmt = stmt.where(True == False)
#
#         data = cursor.execute(stmt).fetchone()
#         try:
#             return data[0]
#         except TypeError:
#             return None
#
#
# def get_types(
#         id: Union[
#             int,
#             List[int],
#             Tuple[int],
#             None,
#         ] = None,
#         system: Union[
#             bool,
#             List[bool],
#             Tuple[bool],
#             None,
#         ] = None,
#         value: Union[
#             str,
#             List[str],
#             Tuple[str],
#             None,
#         ] = None,
# ) -> Union[Tuple[Types], Tuple[None]]:
#     no_data = True
#     with db.context_cursor() as cursor:
#         stmt = select(Types)
#         if id is not None:
#             stmt = stmt.where(Types.id.in_((id,) if isinstance(id, int) else id))
#             no_data = False
#         if system is not None:
#             stmt = stmt.where(Types.system.in_((system,) if isinstance(system, bool) else system))
#             no_data = False
#         if value is not None:
#             stmt = stmt.where(
#                 Types.value.in_((value,) if isinstance(value, str) else value)
#             )
#             no_data = False
#         if no_data:
#             logger.warn(f"No data given for fetching {Types} data. Return All.")
#
#         return cast_data(cursor.execute(stmt).fetchall())


def get_user(
        id: Union[
            int,
            None,
        ] = None,
        tg_uname: Union[
            str,
            None,
        ] = None,
        tg_id: Union[
            int,
            None,
        ] = None,
        create_time: Union[
            datetime,
            None,
        ] = None,
) -> Union[Users, None]:
    no_data = True
    with db.context_cursor() as cursor:
        stmt = select(Users)
        if isinstance(id, int):
            stmt = stmt.where(Users.id == id)
            no_data = False
        if isinstance(tg_uname, str):
            stmt = stmt.where(Users.tg_uname == tg_uname)
            no_data = False
        if isinstance(tg_id, int):
            stmt = stmt.where(Users.tg_id == tg_id)
            no_data = False
        if isinstance(create_time, datetime):
            stmt = stmt.where(Users.create_time == create_time)
            no_data = False
        if no_data:
            logger.warn(f"No data given for fetching {Users} data.")
            stmt = stmt.where(True == False)

        data = cursor.execute(stmt).fetchone()
        try:
            return data[0]
        except TypeError:
            return None


def get_users(
        id: Union[
            int,
            List[int],
            Tuple[int],
            None,
        ] = None,
        tg_uname: Union[
            str,
            List[str],
            Tuple[str],
            None,
        ] = None,
        tg_id: Union[
            int,
            List[int],
            Tuple[int],
            None,
        ] = None,
        create_time: Union[
            datetime,
            List[datetime],
            Tuple[datetime,],
            None,
        ] = None,
) -> Union[Tuple[Users], Tuple[None]]:
    no_data = True
    with db.context_cursor() as cursor:
        stmt = select(Users)
        if id is not None:
            stmt = stmt.where(Users.id.in_((id,) if isinstance(id, int) else id))
            no_data = False
        if tg_uname is not None:
            stmt = stmt.where(
                Users.tg_uname.in_(
                    (tg_uname,) if isinstance(tg_uname, str) else tg_uname
                )
            )
            no_data = False
        if tg_id is not None:
            stmt = stmt.where(
                Users.tg_id.in_((tg_id,) if isinstance(tg_id, int) else tg_id)
            )
            no_data = False
        if create_time is not None:
            stmt = stmt.where(
                Users.create_time.in_(
                    (create_time,) if isinstance(create_time, datetime) else create_time
                )
            )
            no_data = False
        if no_data:
            logger.warn(f"No data given for fetching {Users} data. Return All.")

        return cast_data(cursor.execute(stmt).fetchall())


def get_admin(
        id: Union[
            int,
            Admins.id,
            None,
        ] = None,
        user_id: Union[
            int,
            Admins.user_id,
            Users.id,
            None,
        ] = None,
        create_time: Union[
            datetime,
            Admins.create_time,
            None,
        ] = None,
        create_uid: Union[
            int,
            Admins.create_uid,
            Users.id,
            None,
        ] = None,
        update_time: Union[
            datetime,
            Admins.update_time,
            None,
        ] = None,
        update_uid: Union[
            int,
            Admins.update_uid,
            Users.id,
            None,
        ] = None,
        active: Union[
            bool,
            Admins.active,
            None,
        ] = None,
) -> Union[Admins, None]:
    no_data = True
    with db.context_cursor() as cursor:
        stmt = select(Admins)
        if isinstance(id, int):
            stmt = stmt.where(Admins.id == id)
            no_data = False
        if isinstance(user_id, int):
            stmt = stmt.where(Admins.user_id == user_id)
            no_data = False
        if isinstance(create_time, datetime):
            stmt = stmt.where(Admins.create_time == create_time)
            no_data = False
        if isinstance(create_uid, int):
            stmt = stmt.where(Admins.create_uid == create_uid)
            no_data = False
        if isinstance(update_time, datetime):
            stmt = stmt.where(Admins.update_time == update_time)
            no_data = False
        if isinstance(update_uid, int):
            stmt = stmt.where(Admins.update_uid == update_uid)
            no_data = False
        if isinstance(active, bool):
            stmt = stmt.where(Admins.active == active)
            no_data = False
        if no_data:
            logger.warn(f"No data given for fetching {Admins} data.")
            stmt = stmt.where(True == False)

        data = cursor.execute(stmt).fetchone()
        try:
            return data[0]
        except TypeError:
            return None


def get_admins(
        id: Union[
            int,
            List[int],
            Tuple[int],
            None,
        ] = None,
        user_id: Union[
            int,
            List[int],
            Tuple[int],
            None,
        ] = None,
        create_time: Union[
            datetime,
            List[datetime],
            Tuple[datetime],
            None,
        ] = None,
        create_uid: Union[
            int,
            List[int],
            Tuple[int],
            None,
        ] = None,
        update_time: Union[
            datetime,
            List[datetime],
            Tuple[datetime],
            None,
        ] = None,
        update_uid: Union[
            int,
            List[int],
            Tuple[int],
            None,
        ] = None,
        active: Union[
            bool,
            List[bool],
            Tuple[bool],
            None,
        ] = None,
) -> Union[Tuple[Admins], Tuple[None]]:
    no_data = True
    with db.context_cursor() as cursor:
        stmt = select(Admins)
        if id is not None:
            stmt = stmt.where(Admins.id.in_((id,) if isinstance(id, int) else id))
            no_data = False
        if user_id is not None:
            stmt = stmt.where(
                Admins.user_id.in_((user_id,) if isinstance(user_id, int) else user_id)
            )
            no_data = False
        if create_time is not None:
            stmt = stmt.where(
                Admins.create_time.in_(
                    (create_time,) if isinstance(create_time, datetime) else create_time
                )
            )
            no_data = False
        if create_uid is not None:
            stmt = stmt.where(
                Admins.create_uid.in_(
                    (create_uid,) if isinstance(create_uid, int) else create_uid
                )
            )
            no_data = False
        if update_time is not None:
            stmt = stmt.where(
                Admins.update_time.in_(
                    (update_time,) if isinstance(update_time, datetime) else update_time
                )
            )
            no_data = False
        if update_uid is not None:
            stmt = stmt.where(
                Admins.update_uid.in_(
                    (update_uid,) if isinstance(update_uid, int) else update_uid
                )
            )
            no_data = False
        if active is not None:
            stmt = stmt.where(
                Admins.active.in_((active,) if isinstance(active, bool) else active)
            )
            no_data = False
        if no_data:
            logger.warn(f"No data given for fetching {Admins} data. Return All.")

        return cast_data(cursor.execute(stmt).fetchall())


def get_event(
        id: Union[
            int,
            None,
        ] = None,
        name: Union[
            str,
            None,
        ] = None,
        create_time: Union[
            datetime,
            None,
        ] = None,
        create_uid: Union[
            int,
            None,
        ] = None,
        update_time: Union[
            datetime,
            None,
        ] = None,
        update_uid: Union[
            int,
            None,
        ] = None,
        active: Union[
            bool,
            None,
        ] = None,
) -> Union[Events, None]:
    no_data = True
    with db.context_cursor() as cursor:
        stmt = select(Events)
        if isinstance(id, int):
            stmt = stmt.where(Events.id == id)
            no_data = False
        if isinstance(name, str):
            stmt = stmt.where(Events.name == name)
            no_data = False
        if isinstance(create_time, datetime):
            stmt = stmt.where(Events.create_time == create_time)
            no_data = False
        if isinstance(create_uid, int):
            stmt = stmt.where(Events.create_uid == create_uid)
            no_data = False
        if isinstance(update_time, datetime):
            stmt = stmt.where(Events.update_time == update_time)
            no_data = False
        if isinstance(update_uid, int):
            stmt = stmt.where(Events.update_uid == update_uid)
            no_data = False
        if isinstance(active, bool):
            stmt = stmt.where(Events.active == active)
            no_data = False
        if no_data:
            logger.warn(f"No data given for fetching {Events} data.")
            stmt = stmt.where(True == False)

        data = cursor.execute(stmt).fetchone()
        try:
            return data[0]
        except TypeError:
            return None


def get_events(
        id: Union[
            int,
            List[int],
            Tuple[int],
            None,
        ] = None,
        name: Union[
            str,
            List[str],
            Tuple[str],
            None,
        ] = None,
        create_time: Union[
            datetime,
            List[datetime],
            Tuple[datetime],
            None,
        ] = None,
        create_uid: Union[
            int,
            List[int],
            Tuple[int],
            None,
        ] = None,
        update_time: Union[
            datetime,
            List[datetime],
            Tuple[datetime],
            None,
        ] = None,
        update_uid: Union[
            int,
            List[int],
            Tuple[int],
            None,
        ] = None,
        active: Union[
            bool,
            List[bool],
            Tuple[bool],
            None,
        ] = None,
) -> Union[Tuple[Events], Tuple[None]]:
    no_data = True
    with db.context_cursor() as cursor:
        stmt = select(Events)
        if id is not None:
            stmt = stmt.where(Events.id.in_((id,) if isinstance(id, int) else id))
            no_data = False
        if name is not None:
            stmt = stmt.where(
                Events.name.in_((name,) if isinstance(name, str) else name)
            )
            no_data = False
        if create_time is not None:
            stmt = stmt.where(
                Events.create_time.in_(
                    (create_time,) if isinstance(create_time, datetime) else create_time
                )
            )
            no_data = False
        if create_uid is not None:
            stmt = stmt.where(
                Events.create_uid.in_(
                    (create_uid,) if isinstance(create_uid, int) else create_uid
                )
            )
            no_data = False
        if update_time is not None:
            stmt = stmt.where(
                Events.update_time.in_(
                    (update_time,) if isinstance(update_time, datetime) else update_time
                )
            )
            no_data = False
        if update_uid is not None:
            stmt = stmt.where(
                Events.update_uid.in_(
                    (update_uid,) if isinstance(update_uid, int) else update_uid
                )
            )
            no_data = False
        if active is not None:
            stmt = stmt.where(
                Events.active.in_((active,) if isinstance(active, bool) else active)
            )
            no_data = False
        if no_data:
            logger.warn(f"No data given for fetching {Events} data. Return All.")

        return cast_data(cursor.execute(stmt).fetchall())


def get_action(
        id: Union[
            int,
            None,
        ] = None,
        name: Union[
            str,
            None,
        ] = None,
        event_id: Union[
            int,
            None,
        ] = None,
        create_time: Union[
            datetime,
            None,
        ] = None,
        create_uid: Union[
            int,
            None,
        ] = None,
        update_time: Union[
            datetime,
            None,
        ] = None,
        update_uid: Union[
            int,
            None,
        ] = None,
        active: Union[
            bool,
            None,
        ] = None,
) -> Union[Actions, None]:
    no_data = True
    with db.context_cursor() as cursor:
        stmt = select(Actions)
        if isinstance(id, int):
            stmt = stmt.where(Actions.id == id)
            no_data = False
        if isinstance(name, str):
            stmt = stmt.where(Actions.name == name)
            no_data = False
        if isinstance(event_id, int):
            stmt = stmt.where(Actions.event_id == event_id)
            no_data = False
        if isinstance(create_time, datetime):
            stmt = stmt.where(Actions.create_time == create_time)
            no_data = False
        if isinstance(create_uid, int):
            stmt = stmt.where(Actions.create_uid == create_uid)
            no_data = False
        if isinstance(update_time, datetime):
            stmt = stmt.where(Actions.update_time == update_time)
            no_data = False
        if isinstance(update_uid, int):
            stmt = stmt.where(Actions.update_uid == update_uid)
            no_data = False
        if isinstance(active, bool):
            stmt = stmt.where(Actions.active == active)
            no_data = False
        if no_data:
            logger.warn(f"No data given for fetching {Actions} data.")
            stmt = stmt.where(True == False)

        data = cursor.execute(stmt).fetchone()
        try:
            return data[0]
        except TypeError:
            return None


def get_actions(
        id: Union[
            int,
            List[int],
            Tuple[int],
            None,
        ] = None,
        name: Union[
            str,
            List[str],
            Tuple[str],
            None,
        ] = None,
        event_id: Union[
            int,
            List[int],
            Tuple[int],
            None,
        ] = None,
        create_time: Union[
            datetime,
            List[datetime],
            Tuple[datetime],
            None,
        ] = None,
        create_uid: Union[
            int,
            List[int],
            Tuple[int],
            None,
        ] = None,
        update_time: Union[
            datetime,
            List[datetime],
            Tuple[datetime],
            None,
        ] = None,
        update_uid: Union[
            int,
            List[int],
            Tuple[int],
            None,
        ] = None,
        active: Union[
            bool,
            List[bool],
            Tuple[bool],
            None,
        ] = None,
) -> Union[Tuple[Actions], Tuple[None]]:
    no_data = True
    with db.context_cursor() as cursor:
        stmt = select(Actions)
        if id is not None:
            stmt = stmt.where(Actions.id.in_((id,) if isinstance(id, int) else id))
            no_data = False
        if name is not None:
            stmt = stmt.where(
                Actions.name.in_((name,) if isinstance(name, str) else name)
            )
            no_data = False
        if event_id is not None:
            stmt = stmt.where(
                Actions.event_id.in_(
                    (event_id,) if isinstance(event_id, int) else event_id
                )
            )
            no_data = False
        if create_time is not None:
            stmt = stmt.where(
                Actions.create_time.in_(
                    (create_time,) if isinstance(create_time, datetime) else create_time
                )
            )
            no_data = False
        if create_uid is not None:
            stmt = stmt.where(
                Actions.create_uid.in_(
                    (create_uid,) if isinstance(create_uid, int) else create_uid
                )
            )
            no_data = False
        if update_time is not None:
            stmt = stmt.where(
                Actions.update_time.in_(
                    (update_time,) if isinstance(update_time, datetime) else update_time
                )
            )
            no_data = False
        if update_uid is not None:
            stmt = stmt.where(
                Actions.update_uid.in_(
                    (update_uid,) if isinstance(update_uid, int) else update_uid
                )
            )
            no_data = False
        if active is not None:
            stmt = stmt.where(
                Actions.active.in_((active,) if isinstance(active, bool) else active)
            )
            no_data = False
        if no_data:
            logger.warn(f"No data given for fetching {Actions} data. Return All.")

        return cast_data(cursor.execute(stmt).fetchall())


def get_data(
        id: Union[
            int,
            None,
        ] = None,
        action_id: Union[
            int,
            None,
        ] = None,
        create_time: Union[
            datetime,
            None,
        ] = None,
        create_uid: Union[
            int,
            None,
        ] = None,
        system: Union[
            bool,
            None,
        ] = None,
        type: Union[
            int,
            None,
        ] = None,
        active: Union[
            bool,
            None,
        ] = None,
        value: Union[
            str,
            None,
        ] = None,
) -> Union[Data, None]:
    no_data = True
    with db.context_cursor() as cursor:
        stmt = select(Data)
        if isinstance(id, int):
            stmt = stmt.where(Data.id == id)
            no_data = False
        if isinstance(action_id, int):
            stmt = stmt.where(Data.action_id == action_id)
            no_data = False
        if isinstance(create_time, datetime):
            stmt = stmt.where(Data.create_time == create_time)
            no_data = False
        if isinstance(create_uid, int):
            stmt = stmt.where(Data.create_uid == create_uid)
            no_data = False
        if isinstance(system, bool):
            stmt = stmt.where(Data.system == system)
            no_data = False
        if isinstance(type, int):
            stmt = stmt.where(Data.type == type)
            no_data = False
        if isinstance(active, bool):
            stmt = stmt.where(Data.active == active)
            no_data = False
        if isinstance(value, str):
            stmt = stmt.where(Data.value == value)
            no_data = False
        if no_data:
            logger.warn(f"No data given for fetching {Data} data.")
            stmt = stmt.where(True == False)

        data = cursor.execute(stmt).fetchone()
        try:
            return data[0]
        except TypeError:
            return None


def get_datas(
        id: Union[
            int,
            List[int],
            Tuple[int],
            None,
        ] = None,
        action_id: Union[
            int,
            List[int],
            Tuple[int],
            None,
        ] = None,
        create_time: Union[
            datetime,
            List[datetime],
            Tuple[datetime],
            None,
        ] = None,
        create_uid: Union[
            int,
            List[int],
            Tuple[int],
            None,
        ] = None,
        system: Union[
            bool,
            List[bool],
            Tuple[bool],
            None,
        ] = None,
        type: Union[
            int,
            List[int],
            Tuple[int],
            None,
        ] = None,
        active: Union[
            bool,
            List[bool],
            Tuple[bool],
            None,
        ] = None,
        value: Union[
            str,
            List[str],
            Tuple[str],
            None,
        ] = None,
) -> Union[Tuple[Data], Tuple[None]]:
    no_data = True
    with db.context_cursor() as cursor:
        stmt = select(Data)
        if id is not None:
            stmt = stmt.where(Data.id.in_((id,) if isinstance(id, int) else id))
            no_data = False
        if action_id is not None:
            stmt = stmt.where(
                Data.action_id.in_(
                    (action_id,) if isinstance(action_id, int) else action_id
                )
            )
            no_data = False
        if create_time is not None:
            stmt = stmt.where(
                Data.create_time.in_(
                    (create_time,) if isinstance(create_time, datetime) else create_time
                )
            )
            no_data = False
        if create_uid is not None:
            stmt = stmt.where(
                Data.create_uid.in_(
                    (create_uid,) if isinstance(create_uid, int) else create_uid
                )
            )
            no_data = False
        if system is not None:
            stmt = stmt.where(
                Data.system.in_((system,) if isinstance(system, bool) else system)
            )
            no_data = False
        if type is not None:
            stmt = stmt.where(Data.type.in_((type,) if isinstance(type, str) else type))
            no_data = False
        if active is not None:
            stmt = stmt.where(
                Data.active.in_((active,) if isinstance(active, bool) else active)
            )
            no_data = False
        if value is not None:
            stmt = stmt.where(
                Data.value.in_((value,) if isinstance(value, str) else value)
            )
            no_data = False
        if no_data:
            logger.warn(f"No data given for fetching {Data} data. Return All.")

        return cast_data(cursor.execute(stmt).fetchall())
