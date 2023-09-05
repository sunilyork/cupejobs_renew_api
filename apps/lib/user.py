import fastapi as _fastapi

from apps.config import pwd_context
from apps.db.models.user import User
from apps.lib import helper


async def update_user(user_id: str, user_data: dict):
    put_data = {}
    user = await User.find_one(User.id == user_id)

    if user:
        if len(user_data) < 1:
            return False
        else:
            for k, v in user_data.items():
                if (k == "SISID" and v) or (k == "PAYNO" and v):
                    put_data[k] = helper.encrypt_message(v)
                elif k == "password" and v:
                    if user.verify_password(v):
                        raise _fastapi.HTTPException(
                            status_code=406,
                            detail="Please use different password.",
                        )
                    put_data[k] = pwd_context.hash(v)
                else:
                    put_data[k] = v

        if len(put_data) > 0:
            await user.update({"$set": put_data})
            return True
    return False
