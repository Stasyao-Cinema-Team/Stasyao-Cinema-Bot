from typing import Union

from aiogram.fsm.state import State, StatesGroup

from app.database.models import Events
from app.database.get import get_actions, get_datas
from app.types.type import SystemTypes


def state_group_generator(
        event: Events
):
    actions = get_actions(event_id=event.id)
    event_datas = get_datas(
        action_id=[action.id for action in actions],
        system=True,
        type=event_type
    )
    other_datas = get_datas(
        action_id=[action.id for action in actions],
        system=True,
        type=[_type.id for _type in get_types() if _type.id != event_type.id]
    )

    group = type(
        event.name.lower().replace(' ', '_'),
        (StatesGroup, ),
        {

        }
    )
