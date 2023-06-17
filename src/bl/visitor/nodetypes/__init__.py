from src.bl.visitor.node_processor import Node, get_logger


from src.bl.visitor.nodetypes.array_type_name import ArrayTypeName
from src.bl.visitor.nodetypes.assignment import Assignment
from src.bl.visitor.nodetypes.binary_operation import BinaryOperation
from src.bl.visitor.nodetypes.block import Block
from src.bl.visitor.nodetypes.breakk import Break
from src.bl.visitor.nodetypes.conditional import Conditional
from src.bl.visitor.nodetypes.continuee import Continue
from src.bl.visitor.nodetypes.contract_definition import ContractDefinition
from src.bl.visitor.nodetypes.do_while_statement import DoWhileStatement
from src.bl.visitor.nodetypes.elementary_type_name import ElementaryTypeName
from src.bl.visitor.nodetypes.elementary_type_name_expression import ElementaryTypeNameExpression
from src.bl.visitor.nodetypes.event_definition import EventDefinition
from src.bl.visitor.nodetypes.emit_statement import EmitStatement
from src.bl.visitor.nodetypes.expression_statement import ExpressionStatement
from src.bl.visitor.nodetypes.for_statement import ForStatement
from src.bl.visitor.nodetypes.function_call import FunctionCall
from src.bl.visitor.nodetypes.function_definition import FunctionDefinition
from src.bl.visitor.nodetypes.modifier_definition import ModifierDefinition
from src.bl.visitor.nodetypes.modifier_invocation import ModifierInvocation
from src.bl.visitor.nodetypes.helper import get_stmt_declaration, modify_stmt_children
from src.bl.visitor.nodetypes.identifier import Identifier
from src.bl.visitor.nodetypes.inheritance_specifier import InheritanceSpecifier
from src.bl.visitor.nodetypes.override_specifier import OverrideSpecifier
from src.bl.visitor.nodetypes.if_statement import IfStatement
from src.bl.visitor.nodetypes.index_access import IndexAccess
from src.bl.visitor.nodetypes.literal import Literal
from src.bl.visitor.nodetypes.mapping import Mapping
from src.bl.visitor.nodetypes.member_access import MemberAccess
from src.bl.visitor.nodetypes.new_expression import NewExpression
from src.bl.visitor.nodetypes.parameter_list import ParameterList
from src.bl.visitor.nodetypes.pragma_directive import PragmaDirective
from src.bl.visitor.nodetypes.returnn import Return
from src.bl.visitor.nodetypes.source_unit import SourceUnit
from src.bl.visitor.nodetypes.struct_definition import StructDefinition
from src.bl.visitor.nodetypes.tuple_expression import TupleExpression
from src.bl.visitor.nodetypes.unary_operation import UnaryOperation
from src.bl.visitor.nodetypes.using_for_directive import UsingForDirective
from src.bl.visitor.nodetypes.user_defined_type_name import UserDefinedTypeName
from src.bl.visitor.nodetypes.variable_declaration import VariableDeclaration
from src.bl.visitor.nodetypes.variable_declaration_statement import VariableDeclarationStatement
from src.bl.visitor.nodetypes.while_statement import WhileStatement