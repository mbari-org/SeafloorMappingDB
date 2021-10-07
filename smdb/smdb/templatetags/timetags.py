# https://stackoverflow.com/a/10715876/1281657
from django import template
from datetime import datetime

register = template.Library()


def to_date(esec):
    try:
        dt = datetime.utcfromtimestamp(float(esec))
    except ValueError:
        return None
    return dt.strftime("%d %b %Y")


register.filter(to_date)
