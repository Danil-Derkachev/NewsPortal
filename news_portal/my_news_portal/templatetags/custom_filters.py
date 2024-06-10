from django import template


register = template.Library()


# Регистрируем наш фильтр под именем currency, чтоб Django понимал,
# что это именно фильтр для шаблонов, а не простая функция.
@register.filter()
def shorten(value):
    """
    value: значение, к которому нужно применить фильтр
    """
    if len(value) > 150:
        return f'{value[:150]}...'
    else:
        return f'{value}'


@register.filter()
def censor(value):
    forbidden_words = ('редиска', 'помидор', 'капуста')
    censored_value = ''
    for i in value.split():
        if i in forbidden_words:
            censored_value += i[:1] + '*' * (len(i)-1) + ' '
        else:
            censored_value += i + ' '
    return censored_value
