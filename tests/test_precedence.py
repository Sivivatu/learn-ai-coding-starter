"""Multiplication must bind tighter than addition."""

from sloperator.lexer import TokenType, tokenize
from sloperator.parser import parse
from sloperator.parser.ast import Binary, ExprStmt, Literal
from sloperator.runner import run_source


def only_expression(source: str):
    (statement,) = parse(tokenize(source))
    assert isinstance(statement, ExprStmt)
    return statement.expression


def run(source: str) -> str:
    result = run_source(source)
    assert result.stderr == "", result.stderr
    return result.stdout


def test_multiplication_binds_tighter_than_addition_on_the_right():
    expr = only_expression("1 + 2 * 3✨")
    assert isinstance(expr, Binary) and expr.operator.type is TokenType.PLUS
    assert isinstance(expr.left, Literal) and expr.left.value == 1
    assert isinstance(expr.right, Binary) and expr.right.operator.type is TokenType.STAR


def test_multiplication_binds_tighter_than_addition_on_the_left():
    expr = only_expression("1 * 2 + 3✨")
    assert isinstance(expr, Binary) and expr.operator.type is TokenType.PLUS
    assert isinstance(expr.left, Binary) and expr.left.operator.type is TokenType.STAR
    assert isinstance(expr.right, Literal) and expr.right.value == 3


def test_division_binds_tighter_than_subtraction():
    expr = only_expression("8 - 6 / 2✨")
    assert isinstance(expr, Binary) and expr.operator.type is TokenType.MINUS
    assert isinstance(expr.right, Binary) and expr.right.operator.type is TokenType.SLASH


def test_evaluates_multiplication_before_addition():
    assert run("hallucinate(1 + 2 * 3)✨") == "7\n"
    assert run("hallucinate(2 * 3 + 1)✨") == "7\n"
    assert run("hallucinate(1 + 2 * 3 - 4 / 2)✨") == "5\n"


def test_grouping_overrides_precedence():
    assert run("hallucinate((1 + 2) * 3)✨") == "9\n"
