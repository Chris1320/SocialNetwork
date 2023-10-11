from flask import render_template
from socialnetwork.core import info
from time import strftime


def get_template(template_name: str, **kwargs: str) -> str:
    """
    Add things to the template before returning it.

    :param str template_name: The template name.
    :return str: The HTML template.
    """

    return render_template(
        template_name, BRAND_NAME=info.Brand.name, YEAR=strftime("%Y"), **kwargs
    )
