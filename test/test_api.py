import os

import pytest
from pytest_mock import MockerFixture
from xtb import XtbApi, records
from xtb.exceptions import XtbApiError, XtbSocketError


USER = os.environ['USER']
PASSWORD = os.environ['PASSWORD']


@pytest.fixture(scope='module')
def api():
    with XtbApi() as api:
        api.login(user=USER, password=PASSWORD)
        yield api


def test_connect_raise():
    api = XtbApi()
    api.connect()
    expected_msg = r'Tried to connect\(\) without calling close\(\)'
    with pytest.raises(XtbSocketError, match=expected_msg):
        api.connect()
    api.close()


def test_close_raise():
    api = XtbApi()
    api.connect()
    api.close()
    expected_msg = r'Tried to close\(\) without calling connect\(\)'
    with pytest.raises(XtbSocketError, match=expected_msg):
        api.close()


def test_login():
    with XtbApi() as api:
        out = api.login(user=USER, password=PASSWORD, app_name='Test')
        assert out['status']
        assert 'streamSessionId' in out


def test_logout():
    with XtbApi() as api:
        api.login(user=USER, password=PASSWORD)
        out = api.logout()
    assert out == {'status': True}


def test_api_no_connect():
    api = XtbApi()
    expected_msg = r'Tried to use the API without calling connect\(\) first'
    with pytest.raises(XtbSocketError, match=expected_msg):
        api.get_all_symbols()


def test_api_raises_error(api: XtbApi, mocker: MockerFixture):
    code = 'Dummy code'
    descr = 'Dummy description'
    return_value = {'status': False, 'errorCode': code, 'errorDescr': descr}
    mocker.patch.object(api._connector, '_send_packet')
    mocker.patch.object(
        api._connector, '_get_response', return_value=return_value
    )

    expected_msg = f'There was an error connecting to the API. {code}: {descr}'
    with pytest.raises(XtbApiError, match=expected_msg) as ex:
        api.get_calendar()
        assert ex.value.code == code
        assert ex.value.description == descr


def test_get_all_symbols(api: XtbApi):
    symbols = api.get_all_symbols()
    assert isinstance(symbols, list)
    assert all(isinstance(symbol, records.Symbol) for symbol in symbols)


def test_get_calendar(api: XtbApi):
    calendar = api.get_calendar()
    assert isinstance(calendar, list)
    assert all(isinstance(event, records.Calendar) for event in calendar)


def test_get_symbol(api: XtbApi):
    symbol = api.get_symbol('EURPLN')
    assert isinstance(symbol, records.Symbol)
    assert symbol.symbol == 'EURPLN'


def test_get_chart_last_request(api: XtbApi):
    last_request = api.get_chart_last_request(
        period=5, start=1637698293552, symbol='EURUSD'
    )
    assert isinstance(last_request, records.ChartResponse)


def test_get_chart_range_request(api: XtbApi):
    range_request = api.get_chart_range_request(
        end=1262944412000, period=5, start=1262944112000,
        symbol='EURUSD', ticks=0
    )
    assert isinstance(range_request, records.ChartResponse)


def test_get_commission_def(api: XtbApi):
    comm = api.get_commission_def('EURPLN', 1)
    assert isinstance(comm, records.Commission)
    assert comm.commission == 0.0
    assert comm.rateOfExchange == 1.0


def test_get_current_user(api: XtbApi):
    user = api.get_current_user_data()
    assert isinstance(user, records.User)


def test_get_margin_level(api: XtbApi):
    margin = api.get_margin_level()
    assert isinstance(margin, records.MarginLevel)


def test_get_margin_trade(api: XtbApi):
    margin_trade = api.get_margin_trade('EURPLN', 1)
    assert isinstance(margin_trade, records.MarginTrade)


def test_get_news(api: XtbApi):
    news = api.get_news(0, 1275993488000)
    assert isinstance(news, list)
    assert all(isinstance(v, records.News) for v in news)


def test_get_profit_calculation(api: XtbApi):
    profit = api.get_profit_calculation(
        close_price=1.3, cmd=0, open_price=1.2233, symbol='EURPLN', volume=1.0
    )
    assert isinstance(profit, records.ProfitCalculation)


def test_get_server_time(api: XtbApi):
    time = api.get_server_time()
    assert isinstance(time, records.ServerTime)


def test_get_step_rules(api: XtbApi):
    rules = api.get_step_rules()
    assert isinstance(rules, list)
    assert all(isinstance(v, records.StepRule) for v in rules)


def test_get_tick_prices(api: XtbApi):
    prices = api.get_tick_prices(
        level=0, symbols=['EURPLN'], timestamp=1262944112000
    )
    assert isinstance(prices, records.TickPrices)
    assert len(prices.quotations) == 1


def test_get_trade_records(api: XtbApi):
    trades = api.get_trade_records(orders=[324596785])
    assert len(trades) == 1
    assert isinstance(trades[0], records.Trade)
    assert trades[0].symbol == 'ETHEREUM'
    assert trades[0].order == 324596785


def test_get_trades_opened_only(api: XtbApi):
    trades = api.get_trades(opened_only=True)
    assert len(trades) == 1
    assert isinstance(trades[0], records.Trade)
    assert trades[0].order == 324596785
    assert trades[0].symbol == 'ETHEREUM'


def test_get_trades_closed_only(api: XtbApi):
    trades = api.get_trades(opened_only=False)
    assert len(trades) == 1
    assert isinstance(trades[0], records.Trade)
    assert trades[0].symbol == 'ETHEREUM'
    assert trades[0].order == 324596785


@pytest.mark.skip('Need to fix the start/end times')
def test_get_trades_history(api: XtbApi):
    trades = api.get_trades_history(start=1638732377, end=0)
    assert len(trades) == 2
    assert trades[0].open_time_string == 'Sun Dec 05 21:38:03 CET 2021'
    assert trades[0].order == 76119556
    assert trades[1].open_time_string == 'Sun Dec 05 21:37:21 CET 2021'
    assert trades[1].order == 76119490


def test_get_trading_hours(api: XtbApi):
    trading_hours = api.get_trading_hours(symbols=['EURPLN', 'ETHEREUM'])
    assert len(trading_hours) == 2


def test_get_version(api: XtbApi):
    version = api.get_version()
    assert isinstance(version, records.Version)


def test_ping(api: XtbApi):
    ping = api.ping()
    assert ping
