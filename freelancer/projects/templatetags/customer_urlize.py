import re
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

# Разрешённые домены без протокола
ALLOWED_DOMAINS = [
    r"t\.me",
    r"vk\.com",
    r"vk\.ru",
    r"instagram\.com",
    r"facebook\.com",
    r"max\.ru",
]

# Паттерн:
# 1. Любые ссылки с http/https
# 2. ИЛИ разрешённые домены (с путём или без)
URL_RE = re.compile(
    rf"(?P<url>("
    rf"https?://[^\s<]+"
    rf'|(?:{"|".join(ALLOWED_DOMAINS)})[^\s<]*'
    rf"))",
    re.IGNORECASE,
)


def build_link(url):
    href = url
    if not url.startswith(("http://", "https://")):
        href = "https://" + url

    return (
        f'<a href="{escape(href)}" '
        f'target="_blank" rel="noopener noreferrer nofollow">'
        f"{escape(url)}</a>"
    )


@register.filter
def customer_urlize(value):
    if not value:
        return ""

    text = escape(value)

    def replacer(match):
        url = match.group("url")
        return build_link(url)

    return mark_safe(URL_RE.sub(replacer, text))
