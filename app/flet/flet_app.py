from asyncio import run as async_run
from os import getenv
from typing import Optional

from aiogram.utils.web_app import safe_parse_webapp_init_data
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from flet import DataTable
from flet import IconButton
from flet import icons
from flet import Page
from flet import Row
from flet import Text
from flet.fastapi import app as flet_app
from flet.fastapi import FastAPI
from flet_core import AppBar, ControlEvent, Tooltip, TooltipTriggerMode
from flet_core import colors
from flet_core.types import WebRenderer, TextAlign, MainAxisAlignment
from sqlalchemy import select, join
from uvicorn.config import Config
from uvicorn.server import Server

try:
    from app.logger.logger import Logger
    from app.utils import check_tg_user_is_active_admin
    from app.utils import get_datatable_by_sqlalchemy_data
    from app.utils import generate_events_menu_layout
    from app.utils import create_data_page
    from app.utils import get_sqlalchemy_row_column_names
    from app.utils import get_datacolumns_by_names
    from app.utils import get_datarows_by_column_names
    from app.database.get import get_datas
    from app.database.get import get_user
    from app.flet.layout import AdminPageLayout
    from app.database.models import Data
    from app.database.models import Actions
    from app.database.models import Users
    from app.database.models import Events
    from app.database.connection import Database
    from app.database.connection import cast_data
except ImportError:
    from os.path import dirname, abspath
    from inspect import getfile, currentframe
    from sys import path

    _flet_dir = dirname(abspath(getfile(currentframe())))
    _app_dir = dirname(_flet_dir)
    project_dir = dirname(_app_dir)
    path.insert(0, project_dir)
    del dirname, abspath, getfile, currentframe, path
    from app.logger.logger import Logger
    from app.utils import check_tg_user_is_active_admin
    from app.utils import get_datatable_by_sqlalchemy_data
    from app.utils import generate_events_menu_layout
    from app.utils import create_data_page
    from app.utils import get_sqlalchemy_row_column_names
    from app.utils import get_datacolumns_by_names
    from app.utils import get_datarows_by_column_names
    from app.database.get import get_datas
    from app.database.get import get_user
    from app.flet.layout import AdminPageLayout
    from app.database.models import Data
    from app.database.models import Actions
    from app.database.models import Users
    from app.database.models import Events
    from app.database.connection import Database
    from app.database.connection import cast_data

global _assets_dir

logger = Logger()

fastapi_app = FastAPI()


@fastapi_app.get(path="/", include_in_schema=False, response_class=HTMLResponse)
async def root():
    with open(file=f"{_assets_dir}/root.html", mode='r', encoding='utf-8') as content:
        return HTMLResponse(content=content.read(), status_code=200)


@fastapi_app.post("/login")
async def auth(request: Request):
    form_data = await request.form()
    form_data = form_data.get("Login Form")
    logger.info(f"Recieved form data: \"{form_data}\"")
    return RedirectResponse(url=f"/app?{form_data}", status_code=303)


async def session_handler(page: Page):
    try:
        page.title = "Authorisation Page"
        page.adaptive = True
        page.vertical_alignment = MainAxisAlignment.CENTER

        route = page.route
        local_dev = False
        if '127.0.0.1' in page.url or 'localhost' in page.url:
            local_dev = True
        try:
            init_data = route.split("?")[1]
            TOKEN = getenv("TOKEN")
            if not TOKEN:
                raise KeyError('TOKEN environment variable not set')
            init_data = safe_parse_webapp_init_data(
                token=TOKEN,
                init_data=init_data
            )

            user = init_data.user
            logger.debug(f"Recieved user data: \"{user.id=}\" \"{user.id=}\"")

            if await check_tg_user_is_active_admin(tg_id=user.id):
                return await main(page=page, user=user.__dict__)
            if page.controls:
                page.remove(page.controls)
            return page.add(
                Row(
                    [
                        Text(
                            f"Hello user, {user.first_name} {user.last_name}!\n"
                            f"You haven't got an access to this section.\n"
                            f"Yankee Go Home!!!\n"
                            f"\n"
                            f"Приветствую пользователя, {user.first_name} {user.last_name}!\n"
                            f"У тебя нет доступа в данный раздел.\n"
                            f"Иди Гуляй!!!",
                            text_align=TextAlign.CENTER,
                        )
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    adaptive=True
                )
            )
        except Exception as e:
            if not local_dev:
                raise e
            return await main(page=page, user={"id": 0})

    except Exception as e:
        logger.exception(e)
        if page.controls:
            page.remove(page.controls)
        return page.add(
            Row(
                [
                    Text(
                        f"Hello user!\n"
                        f"You tried to access Admin section from simple browser.\n"
                        f"Return to Telegram and open it as MiniApp.\n"
                        f"\n"
                        f"Приветствую пользователя!\n"
                        f"Вы попытались открыть Админ раздел через обычный браузер.\n"
                        f"Вернитесь в Telegram и откройте страницу, как МиниПриложение.",
                        text_align=TextAlign.CENTER,
                    )
                ],
                alignment=MainAxisAlignment.CENTER,
                adaptive=True
            )
        )


async def main(page: Page, user: Optional[dict] = None):
    if not user:
        user = {}

    system_user = get_user(tg_id=user.get('id'))

    page.title = "Admin Page"
    page.adaptive = True
    page.vertical_alignment = MainAxisAlignment.CENTER
    menu_button = IconButton(icons.MENU)

    page.appbar = AppBar(
        leading=menu_button,
        leading_width=40,
        toolbar_height=40,
        bgcolor=colors.SURFACE_VARIANT,
        adaptive=True
    )
    page.appbar.title = Row(
        controls=[
            Text(
                value="Admin Page",
                size=16,
                text_align=TextAlign.CENTER
            ),
            Text(
                value=f"Logged as {user.get('first_name', 'Unknown')} {user.get('last_name', 'Unknown')}",
                size=16,
                text_align=TextAlign.RIGHT,
                tooltip=Tooltip(
                    message=f"Telegram username: @{system_user.tg_uname}\n"
                            f"Telegram user id: {user.get('id')}\n"
                            f"System user id: {system_user.id}",
                    trigger_mode=TooltipTriggerMode.TAP
                )
            )
        ],
        alignment=MainAxisAlignment.SPACE_BETWEEN,
    )

    async def get_data():
        db = Database()
        with (db.context_cursor() as cursor):
            stmt = select(
                Actions.name,
                Users.tg_uname,
                Data.type,
                Data.active,
                Data.value,
            ).select_from(
                join(
                    Data,
                    Users,
                    Data.create_uid == Users.id
                ).join(
                    Actions,
                    Data.action_id == Actions.id
                ).join(
                    Events,
                    Events.id == Actions.event_id
                )
            ).where(
                Data.active == True,
                Data.system == False
            )

        return cast_data(cursor.execute(stmt).fetchall(), is_table=False)

    async def update_datatable_data(event: ControlEvent):
        parent_controls: list = event.control.parent.controls
        for i in parent_controls:
            if isinstance(i, DataTable):
                _index = parent_controls.index(i)
                parent_controls.remove(i)
                parent_controls.insert(
                    _index,
                    await get_datatable_by_sqlalchemy_data(
                        sqlalchemy_data=await get_data(),
                        hide_columns=['type'],
                        replace_names={
                            "name": "Event | Ивент",
                            "name_1": "Question | Вопрос",
                            "tg_uname": "Telegram Tag | Тег в Телеграм",
                            "value": "Data by User | Данные от Пользователя",
                            "active": "Active Data | Данные Активны",
                        },
                        data_row_max_height=100,
                        data_row_min_height=20
                    )
                )
        await event.page.update_async()

    # event = Events(
    #     id=1,
    #     name="Билет на 15.10.2024",
    #     create_time=datetime.strptime("2024-10-06 19:32:51", "%Y-%m-%d %H:%M:%S"),
    #     create_uid=1,
    #     update_time=datetime.strptime("2024-10-06 19:32:51", "%Y-%m-%d %H:%M:%S"),
    #     update_uid=1,
    #     active=True,
    # )

    # pages = [
    #     (
    #         dict(
    #             icon=icons.SEARCH_OUTLINED,
    #             selected_icon=icons.SEARCH,
    #             label="Data New",
    #         ),
    #         await create_data_page(
    #             title="Data New",
    #             body=Column(
    #                 controls=[
    #                     SearchBar(
    #                         view_elevation=4,
    #                         divider_color=AMBER,
    #                         bar_hint_text="Search User | Поиск пользователя",
    #                         view_hint_text="Select User | Выберите пользователя",
    #                         on_tap=lambda e: e.open_view(),
    #                         controls=[
    #                             ListTile(
    #                                 title=Text(value=),
    #                                 on_click=lambda e: e.control.parent.close_view(text=),
    #                                 data=event
    #                             )
    #                         ]
    #                     ),
    #                     TextButton(
    #                         text="Update Data",
    #                         on_click=update_datatable_data
    #                     ),
    #                     await get_datatable_by_sqlalchemy_data(
    #                         sqlalchemy_data=await get_data(),
    #                         hide_columns=['type'],
    #                         replace_names={
    #                             "name": "Event | Ивент",
    #                             "name_1": "Question | Вопрос",
    #                             "tg_uname": "Telegram Tag | Тег в Телеграм",
    #                             "value": "Data by User | Данные от Пользователя",
    #                             "active": "Active Data | Данные Активны",
    #                         },
    #                         data_row_max_height=100,
    #                         data_row_min_height=20
    #                     )
    #                 ],
    #                 adaptive=True,
    #             ),
    #         ),
    #     ),
    # ]
    pages = await generate_events_menu_layout()

    menu_layout = AdminPageLayout(page, pages)
    await page.add_async(menu_layout)
    menu_button.on_click = lambda e: menu_layout.toggle_navigation()


def start(
        host: str = '0.0.0.0',
        port: int = 8080,
        assets_dir: str = "./app/flet/assets"
):
    global _assets_dir

    _assets_dir = assets_dir
    fastapi_app.mount(
        "/app",
        flet_app(
            session_handler=session_handler,
            assets_dir=_assets_dir,
            upload_dir=None,
            web_renderer=WebRenderer.CANVAS_KIT,
            use_color_emoji=False,
            route_url_strategy="path",
        )
    )
    config = Config(
        app=fastapi_app,
        port=port,
        host=host,
    )
    server = Server(config=config)
    try:
        return server.serve()
    except KeyboardInterrupt:
        pass  # pragma: full coverage


if __name__ == "__main__":
    async_run(
        start(
            host="127.0.0.1",
            assets_dir="./assets"
        )
    )
