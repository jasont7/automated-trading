from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time

class IBApp(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)

	def nextValidId(self, orderId: int):
		super().nextValidId(orderId)
		self.nextorderId = orderId
		print('The next valid order id is: ', self.nextorderId)

	def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
		print('Order Status - orderid:', orderId, 'status:', status, 'filled:', filled, 'remaining:', remaining, 'lastFillPrice:', lastFillPrice)
	
	def openOrder(self, orderId, contract, order, orderState):
		print('Open Order - id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action, order.orderType, order.totalQuantity, orderState.status)

	def execDetails(self, reqId, contract, execution):
		print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)


app = IBApp()
app.connect('127.0.0.1', 4001, 0)

app.nextorderId = None

api_thread = threading.Thread(target=app.run, daemon=True)
api_thread.start()

# Check if the API is connected via orderid
while True:
	if isinstance(app.nextorderId, int):
		print(f'connected - orderId: {app.nextorderId}')
		break
	else:
		print('waiting for connection...')
		time.sleep(1)


def create_stock_contract(symbol):
	contract = Contract()
	contract.symbol = symbol
	contract.secType = 'STK'
	contract.exchange = 'SMART'
	contract.currency = 'USD'
	return contract

def create_stock_order(action='BUY', quantity=1, order_type='MKT', tif='OPG'):
    order = Order()
    order.action = action
    order.totalQuantity = quantity
    order.orderType = order_type
    order.tif = tif  # OPG = order at the opening
    order.eTradeOnly = False
    order.firmQuoteOnly = False
    return order

def place_order(symbol, action, quantity, order_type, tif):
    contract = create_stock_contract(symbol)
    order = create_stock_order(action, quantity, order_type, tif)
    app.placeOrder(app.nextorderId, contract, order)
    app.nextorderId += 1


if __name__ == "__main__":
    place_order('AAPL', 'BUY', 1, 'MKT', 'OPG')
