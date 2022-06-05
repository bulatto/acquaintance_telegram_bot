import re

from constants import PersonInfoEnum

PERSON_INFO_FIELDS = PersonInfoEnum.PERSON_INFO_FIELDS


class PersonInfoValidator:
    """Валидатор полей анкеты пользователя."""

    _person_info = None

    FIELD_ERROR = 'Незаполненно поле: "{field_name}"'

    FIELD_REGEX = r'({field_value}):.+'

    def __init__(self, person_info):
        self._person_info = person_info

    def validate(self):
        """Валидация полей анкеты"""
        fields_errors = []

        for person_info_field in PERSON_INFO_FIELDS.values():
            re_math = re.search(
                self.FIELD_REGEX.format(field_value=person_info_field),
                self._person_info
            )
            if not re_math or not re_math.group(0):
                fields_errors.append(
                    self.FIELD_ERROR.format(field_name=person_info_field)
                )

        if fields_errors:
            return '\n'.join(fields_errors)
