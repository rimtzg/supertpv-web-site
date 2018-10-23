import gettext

gettext.translation('gettext_example', 'locale', fallback=True)
_ = gettext.gettext