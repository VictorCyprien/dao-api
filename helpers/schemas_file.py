from marshmallow import fields, missing

# Custom field that will be omitted from serialized output if the value is None
class OmitNoneField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            # Skip this field in serialization
            return missing
        return super()._serialize(value, attr, obj, **kwargs)