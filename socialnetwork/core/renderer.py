from time import strftime
from typing import Any

from flask import render_template as _render_template

from socialnetwork.core import info


def get_template(template_name: str, **kwargs: Any) -> str:
    """
    Add things to the template before returning it.

    :param str template_name: The template name.
    :return str: The HTML template.
    """

    return _render_template(
        template_name,
        BRAND_NAME=info.Brand.name,
        COPYRIGHT_YEAR=strftime("%Y"),
        **kwargs
    )
