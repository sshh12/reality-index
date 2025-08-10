
Polymarket Documentation home pagedark logo

Search...
⌘K

Ask AI
Main Site

User Guide
For Developers
Changelog
Polymarket
Discord Community
Twitter
Developer Quickstart
Developer Quickstart
Glossary
API Rate Limits
Endpoints
Your First Order
Cancelling Orders
Central Limit Order Book
CLOB Introduction
Deployments
Status
Clients
Authentication
Order Manipulation
Orders Overview
Place Single Order
Place Multiple Orders (Batching)
Get Order
Get Active Orders
Check Order Reward Scoring
Cancel Orders(s)
Onchain Order Info
Trades
Trades Overview
Get Trades
GET
Get Trades (Data-API)
Markets
Get Single Market
Get Markets
Get Sampling Markets
Get Simplified Markets
Get Sampling Simplified Markets
Pricing and Books
GET
Historical Timeseries Data
GET
Get Book
Get Books
GET
Get Price
Get Price(s)
Get Midpoint(s)
Get Spread(s)
Websocket
WSS Overview
WSS Quickstart
WSS Authentication
User Channel
Market Channel
Gamma Markets API
Overview
Gamma Structure
GET
Get Markets
GET
Get Events
Miscellaneous Endpoints
GET
Get User Positions (Data-API)
GET
Get User On-Chain Activity (Data-API)
GET
Get Market Holders (Data-API)
GET
Get Holdings Value (Data-API)
Subgraph
Overview
Resolution
Resolution
Rewards
Liquidity Rewards
Conditional Token Frameworks
Overview
Splitting USDC
Merging Tokens
Reedeeming Tokens
Deployment and Additional Information
Proxy Wallets
Proxy wallet
Negative Risk
Overview
On this page
In addition to detailed comments in the code snippet, here are some more tips to help you get started.
Developer Quickstart
Your First Order
Placing your first order using one of our two Clients is relatively straightforward.
For Python: pip install py-clob-client.
For Typescript: npm install polymarket/clob-client & npm install ethers.
After installing one of those you will be able to run the below code. Take the time to fill in the constants at the top and ensure you’re using the proper signature type based on your login method.

Python First Trade

Typescript First Trade

Copy

Ask AI
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

host: str = "https://clob.polymarket.com"
key: str = "" #This is your Private Key. Export from https://reveal.magic.link/polymarket or from your Web3 Application
chain_id: int = 137 #No need to adjust this
POLYMARKET_PROXY_ADDRESS: str = '' #This is the address listed below your profile picture when using the Polymarket site.

#Select from the following 3 initialization options to matches your login method, and remove any unused lines so only one client is initialized.


### Initialization of a client using a Polymarket Proxy associated with an Email/Magic account. If you login with your email use this example.
client = ClobClient(host, key=key, chain_id=chain_id, signature_type=1, funder=POLYMARKET_PROXY_ADDRESS)

### Initialization of a client using a Polymarket Proxy associated with a Browser Wallet(Metamask, Coinbase Wallet, etc)
client = ClobClient(host, key=key, chain_id=chain_id, signature_type=2, funder=POLYMARKET_PROXY_ADDRESS)

### Initialization of a client that trades directly from an EOA. 
client = ClobClient(host, key=key, chain_id=chain_id)

## Create and sign a limit order buying 5 tokens for 0.010c each
#Refer to the Markets API documentation to locate a tokenID: https://docs.polymarket.com/developers/gamma-markets-api/get-markets

client.set_api_creds(client.create_or_derive_api_creds()) 

order_args = OrderArgs(
    price=0.01,
    size=5.0,
    side=BUY,
    token_id="", #Token ID you want to purchase goes here. 
)
signed_order = client.create_order(order_args)

## GTC(Good-Till-Cancelled) Order
resp = client.post_order(signed_order, OrderType.GTC)
print(resp)

See all 38 lines
​
In addition to detailed comments in the code snippet, here are some more tips to help you get started.
See the Python example for details on the proper way to intialize a Py-Clob-Client depending on your wallet type. Three exhaustive examples are given. If using a MetaMask wallet or EOA please see the resources here, for instructions on setting allowances.
When buying into a market you purchase a “Token” that token represents either a Yes or No outcome of the event. To easily get required token pairs for a given event we have provided an interactive endpoint here.
Common pitfalls:
Negrisk Markets require an additional flag in the OrderArgs negrisk=False
invalid signature error, likely due to one of the following.
Incorrect Funder and or Private Key
Incorrect NegRisk flag in your order arguments
not enough balance / allowance.
Not enough USDC to perform the trade. See the formula at the bottom of this page for details.
If using Metamask / WEB3 wallet go here, for instructions on setting allowances.
Endpoints
Cancelling Orders
github
Powered by Mintlify
Your First Order - Polymarket Documentation


Polymarket Documentation home pagedark logo

Search...
⌘K

Ask AI
Main Site

User Guide
For Developers
Changelog
Polymarket
Discord Community
Twitter
Developer Quickstart
Developer Quickstart
Glossary
API Rate Limits
Endpoints
Your First Order
Cancelling Orders
Central Limit Order Book
CLOB Introduction
Deployments
Status
Clients
Authentication
Order Manipulation
Orders Overview
Place Single Order
Place Multiple Orders (Batching)
Get Order
Get Active Orders
Check Order Reward Scoring
Cancel Orders(s)
Onchain Order Info
Trades
Trades Overview
Get Trades
GET
Get Trades (Data-API)
Markets
Get Single Market
Get Markets
Get Sampling Markets
Get Simplified Markets
Get Sampling Simplified Markets
Pricing and Books
GET
Historical Timeseries Data
GET
Get Book
Get Books
GET
Get Price
Get Price(s)
Get Midpoint(s)
Get Spread(s)
Websocket
WSS Overview
WSS Quickstart
WSS Authentication
User Channel
Market Channel
Gamma Markets API
Overview
Gamma Structure
GET
Get Markets
GET
Get Events
Miscellaneous Endpoints
GET
Get User Positions (Data-API)
GET
Get User On-Chain Activity (Data-API)
GET
Get Market Holders (Data-API)
GET
Get Holdings Value (Data-API)
Subgraph
Overview
Resolution
Resolution
Rewards
Liquidity Rewards
Conditional Token Frameworks
Overview
Splitting USDC
Merging Tokens
Reedeeming Tokens
Deployment and Additional Information
Proxy Wallets
Proxy wallet
Negative Risk
Overview
On this page
REST
Data-API
WebSocket
Developer Quickstart
Endpoints
​
REST
Used for all CLOB REST endpoints, denoted {clob-endpoint}.
https://clob.polymarket.com/
​
Data-API
An additional endpoint that delivers user data, holdings, and other on-chain activities. https://data-api.polymarket.com/
​
WebSocket
Used for all CLOB WSS endpoints, denoted {wss-channel}.
wss://ws-subscriptions-clob.polymarket.com/ws/
API Rate Limits
Your First Order
github
Powered by Mintlify
Endpoints - Polymarket Documentation


Polymarket Documentation home pagedark logo

Search...
⌘K

Ask AI
Main Site

User Guide
For Developers
Changelog
Polymarket
Discord Community
Twitter
Developer Quickstart
Developer Quickstart
Glossary
API Rate Limits
Endpoints
Your First Order
Cancelling Orders
Central Limit Order Book
CLOB Introduction
Deployments
Status
Clients
Authentication
Order Manipulation
Orders Overview
Place Single Order
Place Multiple Orders (Batching)
Get Order
Get Active Orders
Check Order Reward Scoring
Cancel Orders(s)
Onchain Order Info
Trades
Trades Overview
Get Trades
GET
Get Trades (Data-API)
Markets
Get Single Market
Get Markets
Get Sampling Markets
Get Simplified Markets
Get Sampling Simplified Markets
Pricing and Books
GET
Historical Timeseries Data
GET
Get Book
Get Books
GET
Get Price
Get Price(s)
Get Midpoint(s)
Get Spread(s)
Websocket
WSS Overview
WSS Quickstart
WSS Authentication
User Channel
Market Channel
Gamma Markets API
Overview
Gamma Structure
GET
Get Markets
GET
Get Events
Miscellaneous Endpoints
GET
Get User Positions (Data-API)
GET
Get User On-Chain Activity (Data-API)
GET
Get Market Holders (Data-API)
GET
Get Holdings Value (Data-API)
Subgraph
Overview
Resolution
Resolution
Rewards
Liquidity Rewards
Conditional Token Frameworks
Overview
Splitting USDC
Merging Tokens
Reedeeming Tokens
Deployment and Additional Information
Proxy Wallets
Proxy wallet
Negative Risk
Overview

Python

Typescript

Copy

Ask AI
resp = client.get_markets(next_cursor = "")
print(resp)
print("Done!")
Markets
Get Markets
Get available CLOB markets (paginated).
HTTP REQUEST
GET /<clob-endpoint>/markets?next_cursor=<next_cursor>
​
Request Parameters
Name	Required	Type	Description
next_cursor	no	string	cursor to start with, used for traversing paginated response
​
Response Format
Name	Type	Description
limit	number	limit of results in a single page
count	number	number of results
next_cursor	string	pagination item to retrieve the next page base64 encoded. ‘LTE=’ means the end and empty (”) means the beginning
data	Market[]	list of markets
A Market object is of the form:
Name	Type	Description
condition_id	string	id of market which is also the CTF condition ID
question_id	string	question id of market which is the CTF question ID which is used to derive the condition_id
tokens	Token[2]	binary token pair for market
rewards	Rewards	rewards related data
minimum_order_size	string	minimum limit order size
minimum_tick_size	string	minimum tick size in units of implied probability (max price resolution)
category	string	market category
end_date_iso	string	iso string of market end date
game_start_time	string	iso string of game start time which is used to trigger delay
question	string	question
market_slug	string	slug of market
min_incentive_size	string	minimum resting order size for incentive qualification
max_incentive_spread	string	max spread up to which orders are qualified for incentives (in cents)
active	boolean	boolean indicating whether market is active/live
closed	boolean	boolean indicating whether market is closed/open
seconds_delay	integer	seconds of match delay for in-game trade
icon	string	reference to the market icon image
fpmm	string	address of associated fixed product market maker on Polygon network
Where the Token object is of the form:
Name	Type	Description
token_id	string	erc1155 token id
outcome	string	human readable outcome
Where the Rewards object is of the form:
Name	Type	Description
min_size	number	min size of an order to score
max_spread	number	max spread from the midpoint until an order scores
event_start_date	string	string date when the event starts
event_end_date	string	string date when the event ends
in_game_multiplier	number	reward multiplier while the game has started
reward_epoch	number	current reward epoch
Get Single Market
Get Sampling Markets
github
Powered by Mintlify
Get Markets - Polymarket Documentation


Polymarket Documentation home pagedark logo

Search...
⌘K

Ask AI
Main Site

User Guide
For Developers
Changelog
Polymarket
Discord Community
Twitter
Developer Quickstart
Developer Quickstart
Glossary
API Rate Limits
Endpoints
Your First Order
Cancelling Orders
Central Limit Order Book
CLOB Introduction
Deployments
Status
Clients
Authentication
Order Manipulation
Orders Overview
Place Single Order
Place Multiple Orders (Batching)
Get Order
Get Active Orders
Check Order Reward Scoring
Cancel Orders(s)
Onchain Order Info
Trades
Trades Overview
Get Trades
GET
Get Trades (Data-API)
Markets
Get Single Market
Get Markets
Get Sampling Markets
Get Simplified Markets
Get Sampling Simplified Markets
Pricing and Books
GET
Historical Timeseries Data
GET
Get Book
Get Books
GET
Get Price
Get Price(s)
Get Midpoint(s)
Get Spread(s)
Websocket
WSS Overview
WSS Quickstart
WSS Authentication
User Channel
Market Channel
Gamma Markets API
Overview
Gamma Structure
GET
Get Markets
GET
Get Events
Miscellaneous Endpoints
GET
Get User Positions (Data-API)
GET
Get User On-Chain Activity (Data-API)
GET
Get Market Holders (Data-API)
GET
Get Holdings Value (Data-API)
Subgraph
Overview
Resolution
Resolution
Rewards
Liquidity Rewards
Conditional Token Frameworks
Overview
Splitting USDC
Merging Tokens
Reedeeming Tokens
Deployment and Additional Information
Proxy Wallets
Proxy wallet
Negative Risk
Overview

Python

Typescript

Copy

Ask AI
resp = client.get_market(condition_id = "...")
print(resp)
print("Done!")
Markets
Get Single Market
​
Get Market
Get a single CLOB market.
HTTP REQUEST
GET /<clob-endpoint>/markets/<condition_id>
​
Response Format
Name	Type	Description
market	Market	market object
Get Trades (Data-API)
Get Markets
github
Powered by Mintlify
Get Single Market - Polymarket Documentation