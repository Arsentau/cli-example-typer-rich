from math import pow

from entities.currencies import Currency, OperationType
from rich.console import Console
from rich.style import Style
from rich.table import Table
from services.api_consumer import Exchange


class Calculator:
    def __init__(
        self,
        console: Console,
        from_currency: Currency,
        to_currency: Currency,
        amount: float,
        exchange: Exchange
    ) -> None:
        self.console = console
        self.from_currency = from_currency.value
        self.to_currency = to_currency.value
        self.amount = amount
        self._exchange_data: dict = exchange.data
        self.converted_value = None
        self._exchange_value = None

    def _get_exchange_value(self) -> None:
        match self.from_currency:
            case Currency.ARS.value:
                self._exchange_value = pow(
                    self._exchange_data
                    .get(self.to_currency)
                    .get(OperationType.SELL.value),
                    -1
                )
            case _:
                self._exchange_value = self._exchange_data \
                    .get(self.from_currency) \
                    .get(OperationType.BUY.value)

    def convert(self) -> None:
        self._get_exchange_value()
        self.converted_value = self.amount * self._exchange_value


class CalculatorLogger:
    def __init__(self, calc: Calculator) -> None:
        self.calculator = calc
        self.logger()

    def logger(self) -> None:
        console = self.calculator.console

        table = Table()
        table.add_column(
            "FROM",
            justify="center",
            width=30,
            header_style=Style(color="blue", bold=True),
            style=Style(
                color="blue"
            )
        )
        table.add_column(
            "TO",
            justify="center",
            width=30,
            header_style=Style(color="green", bold=True),
            style=Style(
                color="green",
                bold=True
            )
        )

        table.add_row(
            self.calculator.from_currency.upper(),
            self.calculator.to_currency.upper(),

        )
        table.add_row(
            str(self.calculator.amount),
            str(self.calculator.converted_value)
        )

        console.print(table)
