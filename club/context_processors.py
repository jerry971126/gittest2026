from .models import User

ROLE_NAMES = {
    0: '學生',
    1: '社長',
    2: '指導老師',
    3: '訓育組',
}


def current_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return {'current_user': None, 'current_user_role': None}

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return {'current_user': None, 'current_user_role': None}

    return {
        'current_user': user,
        'current_user_role': ROLE_NAMES.get(user.us_rank, '未知身份'),
    }
