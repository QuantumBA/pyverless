class Serializer(object):

    include = []
    exclude = []
    properties = '__dict__'

    def __init__(self, instance=None, **kwargs):
        """
        constructor
        """
        self.instance = instance

    def to_representation(self, instance):
        """
        A dictionary representation of model properties.
        * if include (a list of keys) is provided just the desired keys are
          included in the dictionary.
        * if exclude (a list of keys) is provided the desired keys are
          excluded from the dictionary.
        """
        if self.include:
            return {k: v for k, v in getattr(instance, self.properties).items() if k in self.include}
        elif self.exclude:
            return {k: v for k, v in getattr(instance, self.properties).items() if k not in self.exclude}
        else:
            return getattr(instance, self.properties).copy()

    @property
    def data(self):
        return self.to_representation(self.instance)
