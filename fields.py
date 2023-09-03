
class Field:
    def __init__(self, required=False, nullable=True):
        self.required = required
        self.nullable = nullable
        self.value = None

    def validate(self, value):
        ...


class CharField(Field):

    def validate(self, value):
        if not (type(value) == str):
            raise ValueError('Char Field got non-string type')


class DigitField(Field):

    def validate(self, value):
        if not (type(value) == int):
            raise ValueError('Char Digit got non-digit type')


class DateField(Field):
    pass


class ArgumentsField(CharField):
    pass


class EmailField(CharField):
    pass


class PhoneField(DigitField):
    pass


class BirthDayField(DateField):
    pass


class GenderField(CharField):
    pass


class ClientIDsField(CharField):
    pass
