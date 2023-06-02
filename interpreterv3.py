from classv2 import ClassDef
from intbase import InterpreterBase, ErrorType
from bparser import BParser, StringWithLineNumber
from objectv2 import ObjectDef
from type_valuev2 import TypeManager
import copy


# def read_file(filename):
#     lines = []
#     with open(filename, 'r') as file:
#         for line in file:
#             lines.append(line.strip())
#     return lines


# program_source = read_file(
#     'FILE_NAME_HERE')


# need to document that each class has at least one method guaranteed

# Main interpreter class
class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output
        self.exception = None

    # run a program, provided in an array of strings, one string per line of source code
    # usese the provided BParser class found in parser.py to parse the program into lists
    def get_exception(self):
        return self.exception

    def create_exception(self, exception):
        self.exception = exception

    def run(self, program):
        status, parsed_program = BParser.parse(program)
        if not status:
            super().error(
                ErrorType.SYNTAX_ERROR, f"Parse error on program: {parsed_program}"
            )
        self.__add_all_class_types_to_type_manager(parsed_program)
        self.__map_class_names_to_class_defs(parsed_program)

        # instantiate main class
        invalid_line_num_of_caller = None
        self.main_object = self.instantiate(
            InterpreterBase.MAIN_CLASS_DEF, invalid_line_num_of_caller
        )

        # call main function in main class; return value is ignored from main
        self.main_object.call_method(
            InterpreterBase.MAIN_FUNC_DEF, [], False, invalid_line_num_of_caller
        )

        # program terminates!

    # user passes in the line number of the statement that performed the new command so we can generate an error
    # if the user tries to new an class name that does not exist. This will report the line number of the statement
    # with the new command
    def instantiate(self, class_name, line_num_of_statement):
        if class_name not in self.class_index:
            super().error(
                ErrorType.TYPE_ERROR,
                f"No class named {class_name} found",
                line_num_of_statement,
            )
        class_def = self.class_index[class_name]
        obj = ObjectDef(
            self, class_def, None, self.trace_output
        )  # Create an object based on this class definition
        return obj

    # def replace_template_args(self, lst, template_args, fields_to_replace):
    #     for i, item in enumerate(lst[3:], 3):
    #         if isinstance(item, list):
    #             self.replace_template_args(
    #                 item, template_args, fields_to_replace)
    #         elif isinstance(item, str) and item in fields_to_replace:
    #             lst[i] = fields_to_replace[item]

    #     print(lst)

    def replace_nested_array(self, arr, old_string, new_string):
        if isinstance(arr, list):
            for i in range(len(arr)):
                if isinstance(arr[i], list):
                    self.replace_nested_array(
                        arr[i], old_string, new_string)
                elif isinstance(arr[i], str):
                    temp = StringWithLineNumber(arr[i].replace(
                        old_string, new_string), 0)
                    arr[i] = temp
        print(arr)

    def instantiate_templated_class(self, class_name, line_num_of_statement, template_args, actual_full_class_name):
        fields_to_replace_map = {}
        if class_name not in self.tclass_index:
            super().error(
                ErrorType.TYPE_ERROR,
                f"No templated class named {class_name} found",
                line_num_of_statement,
            )
        tclass_def = self.tclass_index[class_name]
        fields_to_replace = tclass_def[2]

        if len(fields_to_replace) != len(template_args):
            super().error(ErrorType.TYPE_ERROR)
        for i in range(len(fields_to_replace)):
            fields_to_replace_map[fields_to_replace[i]] = template_args[i]

        temp_tclass_def = copy.deepcopy(tclass_def)
        for field_replace in fields_to_replace_map:
            self.replace_nested_array(temp_tclass_def, field_replace,
                                      fields_to_replace_map[field_replace])
        # self.replace_template_args(
        #     temp_tclass_def, template_args, fields_to_replace_map)
        temp_tclass_def[1] = actual_full_class_name
        del temp_tclass_def[2]
        self.type_manager.add_class_type(actual_full_class_name, None)
        obj = ClassDef(temp_tclass_def, self)
        self.class_index[actual_full_class_name] = obj
        instantiatedObj = self.instantiate(
            actual_full_class_name, line_num_of_statement)
        return instantiatedObj

    # returns a ClassDef object
    def get_class_def(self, class_name, line_number_of_statement):
        if class_name not in self.class_index:
            super().error(
                ErrorType.TYPE_ERROR,
                f"No class named {class_name} found",
                line_number_of_statement,
            )
        return self.class_index[class_name]

    # returns a bool
    def is_valid_type(self, typename):
        return self.type_manager.is_valid_type(typename)

    # returns a bool
    def is_a_subtype(self, suspected_supertype, suspected_subtype):
        return self.type_manager.is_a_subtype(suspected_supertype, suspected_subtype)

    # typea and typeb are Type objects; returns true if the two type are compatible
    # for assignments typea is the type of the left-hand-side variable, and typeb is the type of the
    # right-hand-side variable, e.g., (set person_obj_ref (new teacher))
    def check_type_compatibility(self, typea, typeb, for_assignment=False):
        return self.type_manager.check_type_compatibility(typea, typeb, for_assignment)

    def __map_class_names_to_class_defs(self, program):
        self.class_index = {}
        self.tclass_index = {}
        for item in program:
            if item[0] == InterpreterBase.CLASS_DEF:
                if item[1] in self.class_index:
                    super().error(
                        ErrorType.TYPE_ERROR,
                        f"Duplicate class name {item[1]}",
                        item[0].line_num,
                    )
                self.class_index[item[1]] = ClassDef(item, self)
            elif item[0] == InterpreterBase.TEMPLATE_CLASS_DEF:
                if item[1] in self.class_index:
                    super().error(
                        ErrorType.TYPE_ERROR,
                        f"Duplicate class name {item[1]}",
                        item[0].line_num,
                    )
                valueItem = copy.deepcopy(item)
                valueItem[0] = InterpreterBase.CLASS_DEF
                self.tclass_index[item[1]] = valueItem

    # [class classname inherits superclassname [items]]
    def __add_all_class_types_to_type_manager(self, parsed_program):
        self.type_manager = TypeManager()
        for item in parsed_program:
            if item[0] == InterpreterBase.CLASS_DEF:
                class_name = item[1]
                superclass_name = None
                if item[2] == InterpreterBase.INHERITS_DEF:
                    superclass_name = item[3]
                self.type_manager.add_class_type(class_name, superclass_name)

            if item[0] == InterpreterBase.TEMPLATE_CLASS_DEF:
                class_name = item[1]
                self.type_manager.add_tclass_type(class_name)


if __name__ == '__main__':
    intepreter = Interpreter()
    intepreter.run(program_source)

    print(f"FULLL OUTPUTTTT {intepreter.get_output()}")
