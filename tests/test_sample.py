import pytest
import logging
import datetime
from telegram import Update, Message, User
from telegram import Location
from infoFunctions import choose_location, test_get_location

LOGGER = logging.getLogger(__name__)

# def func(x):
#     return x+1


# def test_answer():
#     assert func(3) == 5


# # content of test_class.py
# class TestClass:
#     def test_one(self):
#         x = "this"
#         assert "h" in x

#     def test_two(self):
#         x = "hello"
#         assert hasattr(x, "check")
# create a telegram location
location = Location(-177.05691 , 22.85983)


# create a telegram message
message = Message(
    message_id=1,
    date=datetime.datetime(2021, 1, 1, 0, 0, 0),
    chat=None,
    from_user=User(1, "", False),
    text="test",
    location=location
)

# create a telegram update
update = Update(
    1,
    message=message,
    edited_message=None,
    channel_post=None,
    edited_channel_post=None,
    inline_query=None,
    chosen_inline_result=None,
    callback_query=None,
    shipping_query=None,
    pre_checkout_query=None,
    poll=None,
    poll_answer=None,
    my_chat_member=None,
    chat_member=None,
)

@pytest.mark.asyncio
class TestTelegram:
    async def test_sample(self):
        res = await test_get_location(update, None)
        LOGGER.info(res)
