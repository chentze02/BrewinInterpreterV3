from classv2 import ClassDef


class TemplatedClassDef(ClassDef):
    def __init__(self, class_source, interpreter):
        super().__init__(class_source, interpreter)
        self.parameterized_types = self.__extract_parameterized_types(
            class_source[1])

    def __extract_parameterized_types(self, class_name):
        parameterized_types = []
        if "@" in class_name:
            parameterized_types = class_name.split("@")[1:]
        return parameterized_types

    def get_parameterized_types(self):
        return self.parameterized_types

    def replace_parameterized_types(self, instantiated_types):
        replaced_class_name = self.name
        for i in range(len(self.parameterized_types)):
            replaced_class_name = replaced_class_name.replace(
                "@" + self.parameterized_types[i], "@" + instantiated_types[i]
            )
        return replaced_class_name
