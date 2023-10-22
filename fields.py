from datetime import datetime
from typing import Dict, List


class ValidationError(ValueError):
    message = ""


class Field:
    def __init__(self, value=None, required=False, nullable=True):
        self.required = required
        self.nullable = nullable
        self.value = value

    def base_validate(self, value):
        if not self.nullable and value is None:
            raise ValidationError("Expected not None")
        if self.required and not value:
            raise ValidationError("Field is required")

    def validate(self, value):
        ...


class CharField(Field):

    def validate(self, value):
        if not (type(value) == str):
            raise ValidationError('Char Field got non-string type')


class DigitField(Field):

    def validate(self, value):
        if not (type(value) == int):
            raise ValidationError('Digit field got non-digit type')


class DateField(Field):

    def validate(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y")
        except ValidationError:
            raise ValidationError("Date field don't match format: DD.MM.YYYY")


class EmailField(Field):

    def validate(self, value):
        if "@" not in value:
            raise ValidationError('Email field got not valid email')


class PhoneField(Field):

    def validate(self, value):
        if len(str(value)) != 11 or str(value)[0] != 7:
            raise ValidationError('Phone field not valid phone number')


class BirthDayField(DateField):

    def validate(self, value):
        super().validate(value)
        if (datetime.now() - self.date).days/365 >= 70:
            raise ValidationError('More than 70 years have passed since birth date')

        elif (datetime.now() - self.date).days/365 < 0:
            raise ValidationError('You have not born yet')


class GenderField(DigitField):

    def validate(self, value):
        super().validate(value)
        if self.value not in [0, 1, 2]:
            raise ValidationError("Gender field don't match next values: 0, 1, 2")


class ClientIDsField(Field):

    def validate(self, value):
        if not isinstance(value, List):
            raise ValidationError("ClientIDs field is not valid List type")

        for val in value:
            if not isinstance(val, int):
                raise ValidationError(
                    "At least one element of ClientIDs array is not valid "
                    "integer type")


class ArgumentsField(Field):

    def validate(self, value):
        if not isinstance(value, Dict):
            raise ValidationError('Arguments field is not valid dict (json)')
