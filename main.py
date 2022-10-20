from entities.currencies import Currency
from rich.console import Console
from rich.progress import track
from services.api_consumer import Exchange
from services.calculator import Calculator, CalculatorLogger
from tables.exchange import exchange_table_gen
from typer import Typer

app = Typer()


@app.command()
def currencies(
    euro: bool = True,
    official: bool = True
):
    """This command retrieves the values from an api
    https://bluelytics.com.ar/#!/api
    """
    exchange = None
    for i in track(range(3), description="Fetching..."):
        exchange = Exchange()
    options = (euro, official)

    match options:
        case (True, False):
            del exchange.data['oficial']
            del exchange.data['oficial_euro']
        case (False, True):
            del exchange.data['oficial_euro']
            del exchange.data['blue_euro']
        case (False, False):
            del exchange.data['oficial']
            del exchange.data['oficial_euro']
            del exchange.data['blue_euro']

    table = exchange_table_gen(exchange.data)
    console = Console()
    console.print(
        ":heavy_check_mark: :thumbs_up: :tada: :100: Last update: " +
        exchange.data["last_update"][:-6]
    )
    console.print(table)


@app.command()
def conversion(json_response: bool = False):
    console = Console()

    try:
        exchange = Exchange()
        console.print("Updated :heavy_check_mark:", style="bold blue")
    except Exception as e:
        console.print_exception()
        raise e
    if json_response:
        console.print_json(exchange.json_data.content.decode('utf8'))

    amount = 0
    from_currency = None
    to_currency = None
    currency_names = [data.name for data in Currency]

    while (
        amount == 0 or
        not from_currency or
        not to_currency
    ):
        if not from_currency:
            console.print(currency_names)
            console.print("Original currency", style="bold green")
            command = input("FROM: ").upper()
            if len(command.split()) > 1 or not (command in currency_names):
                console.print(
                    "Invalid value, please try again",
                    style="bold red"
                )
                continue
            from_currency = Currency[command]
            if from_currency is not Currency.ARS:
                to_currency = Currency.ARS

        if not to_currency:
            console.print(currency_names)
            console.print("Destination currency", style="bold green")
            command = input("TO: ").upper()
            if (len(command.split()) > 1) or \
                not (command in currency_names) or \
                    (command == from_currency):
                console.print(
                    "Invalid value, please try again",
                    style="bold red"
                )
                continue
            to_currency = Currency[command]

        if amount == 0:
            console.print(
                "Introduce the amount in "
                f"{from_currency.name.upper()} to be converted to {to_currency.name.upper()}",
                style="bold green"
            )
            command = input("AMOUNT: ")
            try:
                amount = float(command)
            except ValueError:
                console.print(
                    "Invalid value, please try again",
                    style="bold red"
                )
                continue
        break
    calculator = Calculator(
        console=console,
        from_currency=from_currency,
        to_currency=to_currency,
        amount=amount,
        exchange=exchange
    )
    calculator.convert()
    CalculatorLogger(calculator)


if __name__ == '__main__':
    app()
