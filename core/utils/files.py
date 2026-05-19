import uuid
from datetime import datetime
from pathlib import Path


def user_avatar_upload_path(instance, filename):
    extension = Path(filename).suffix

    filename = f'{uuid.uuid4().hex}{extension}'

    return (
        f'core/users/avatars/'
        f'{datetime.now().strftime("%Y/%m")}/'
        f'{filename}'
    )
