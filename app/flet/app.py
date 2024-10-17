from asyncio import run

from flet import IconButton, Page, Row, TextField, icons, app_async, AppView
from flet_core import ControlEvent
from telegram_webapp_auth.auth import TelegramUser, TelegramAuthenticator


async def main(page: Page):
    page.title = "Admin Page"
    page.adaptive = True
    page.vertical_alignment = "center"

    txt_number = TextField(value="0", text_align="center", width=100)

    async def minus_click(event: ControlEvent):
        txt_number.value = str(int(txt_number.value) - 1)
        page.update()

    async def plus_click(event: ControlEvent):
        txt_number.value = str(int(txt_number.value) + 1)
        page.update()

    page.add(
        Row(
            [
                IconButton(icons.REMOVE, on_click=minus_click),
                txt_number,
                IconButton(icons.ADD, on_click=plus_click),
            ],
            alignment="center",
        )
    )


async def start(
        port: int,
        assets_dir: str = "./app/flet/assets"
):
    await app_async(target=main, port=port, view=AppView.WEB_BROWSER, assets_dir=assets_dir)


if __name__ == "__main__":
    run(
        start(
            port=8080,
            assets_dir="./assets"
        )
    )
