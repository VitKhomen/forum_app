from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


# ── Коментарі ──────────────────────────────────────────────────

class CommentCreateMinuteThrottle(UserRateThrottle):
    """5 коментарів на хвилину"""
    scope = 'comment_create_minute'


class CommentCreateHourThrottle(UserRateThrottle):
    """30 коментарів на годину"""
    scope = 'comment_create_hour'


# ── Лайки ──────────────────────────────────────────────────────

class LikeToggleMinuteThrottle(UserRateThrottle):
    """20 лайків на хвилину"""
    scope = 'like_toggle_minute'


class LikeToggleDayThrottle(UserRateThrottle):
    """200 лайків на день"""
    scope = 'like_toggle_day'


# ── Пости ──────────────────────────────────────────────────────

class PostCreateMinuteThrottle(UserRateThrottle):
    """3 пости на хвилину"""
    scope = 'post_create_minute'


class PostCreateDayThrottle(UserRateThrottle):
    """20 постів на день"""
    scope = 'post_create_day'


# ── Авторизація (захист від брутфорсу) ────────────────────────

class LoginRateThrottle(AnonRateThrottle):
    """5 спроб входу на хвилину з одного IP"""
    scope = 'login'


class RegisterRateThrottle(AnonRateThrottle):
    """3 реєстрації на годину з одного IP"""
    scope = 'register'


# ── Закладки ───────────────────────────────────────────────────

class BookmarkThrottle(UserRateThrottle):
    scope = 'bookmark'
