# INFO: This file contains the StockTradeManager class that is used to manage stock trades, bids and sell offers
import sqlite3
from datetime import datetime
import requests
import time

from StockModules import *
from Utils import *

# INFO: Manages stock trades, bids and sell offers
# it can be used to add, remove, update and get trades
# Consider this as a singleton
# Implementation:
# We start by matching bids with sell offers by the highest offer price and the lowest bid price
# (Similar to how RuneScape's Grand Exchange works)
# given that the trades are always made when a new offer or bid is added
# the system will always be up to date unless the stock market price changes
# when the stock market price changes we update the whole system and match bids with sell offers
class StockTradeManager:
    cached_data = []  # NOTE: This stores cached data for every tradeable stock in the system, consists of id, price and when the last price was fetched
                      # TODO: check and fill in the rest of the above ^ comment

    trades = []     # Already made trades

    # Both of these shouldn't store bids or selloffers that could be matched
    # unless the stock price has just changed, that's why we keep track of them on the server
    bids = []       # Bids that are waiting to be matched with sell offers
    sell_offers = [] # Sell offers that are waiting to be matched with bids
    # current_stock = None # The current stock price of the current stock that is being traded NOTE: this should be set to the price of the stock that is being traded before update is called
    current_stock = float(0.0) # The current stock price of the current stock that is being traded NOTE: this should be set to the price of the stock that is being traded before update is called

    def __init__(self):
        self.trades = []
        self.bids = []
        self.sell_offers = []

        # Query the database for the current stock price
        conn = sqlite3.connect('Database/Main.db')
        # Fetch apple stock price
        cursor = conn.execute("SELECT * FROM stocks")
        # stock = cursor.fetchone()[0]

        # TODO: Use a stock object atm we just the stock price float 
        stocks = []
        for row in cursor:
            stocks.append(row)

        for stock in stocks:
            # self.current_stock = Stock(stock[0], stock[1], stock[2], stock[3])

            # TODO: Get the current stock price from the REST API if the time since the last fetch is greater than 1 hour etc.

            # if (self.current_stock == Stock()):
            #     print("ERROR: Failed to fetch the current stock price from the database!")

            try:
                self.current_stock = float(stock[2])
            except ValueError:
                print(f"Cannot convert '{stock[2]}' to float")

            # self.current_stock = float(stock[2])
            print("Current stock price: ${}".format(self.current_stock))

            # Check that the stock price is fetched within the last hour
            # if not, fetch the stock price from the REST API and update the current stock price
            time = datetime.now() # NOTE: We fetch time here to avoid any possible time differences between the stock price and the time we fetch it as this might take time

            # Convert the fetched time to a datetime object
            stock_time = datetime.strptime(str(stock[3]), '%Y-%m-%d %H:%M:%S.%f')

            # TODO: Init a timer with an event that will update the stock price every hour
            # Check if the stock price is fetched within the last hour
            if (time - stock_time).total_seconds() > 3600:
            # if True:
                # Fetch the stock price from the REST API
                res = requests.get('https://api.marketdata.app/v1/stocks/quotes/AAPL/')
                data = res.json()

                # Update the current stock price
                try:
                    self.current_stock = float(data['last'][0])
                except ValueError:
                    print(f"Cannot convert '{stock[2]}' to float")

                cursor = conn.execute("UPDATE stocks SET current_price = ?, fetched_at = ? WHERE id = ?", (self.current_stock, time, int(stock[0])))
                conn.commit()

                print("Updated current stock price: ${} and time: {}".format(self.current_stock, time))

        # Query the database for bids
        cursor = conn.execute("SELECT * FROM BIDS")
        bids = []
        for row in cursor:
            bids.append(row)
        cursor.close()

        for bid in bids:
            self.bids.append(Order(bid[0], User(bid[1]), bid[2], bid[3], bid[4], bid[5]))

        # Query the database for sell offers
        cursor = conn.execute("SELECT * FROM OFFERS")
        sell_offers = []
        for row in cursor:
            sell_offers.append(row)

        for sell_offer in sell_offers:
            self.sell_offers.append(Order(sell_offer[0], User(sell_offer[1]), sell_offer[2], sell_offer[3], sell_offer[4], sell_offer[5], 1))

        # Query the database for trades
        cursor = conn.execute("SELECT * FROM TRADES")
        trades = []
        for row in cursor:
            trades.append(row)

        for trade in trades:
            self.trades.append(Trade(trade[0], trade[1], trade[2], trade[3], trade[4], trade[5]))

        # Clean up
        cursor.close()
        conn.close()

    # Adds a new trade to the trades list
    # NOTE: This is called when a bid is matched with a sell offer with a valid price
    # and a transaction has already been made and added to the database
    def add_trade(self, bid : Order, sellOffer : Order, time : datetime):

        pass

    # Adds a new sell offer and updates
    def add_offer(self, newOffer : Order):
        self.sell_offers.append(newOffer)
        self.update()

        possibly_matching_bids = []
        for bid in self.bids:
            if bid.price >= newOffer.price and newOffer.stock_id == newOffer.stock_id and bid.user.id != newOffer.user.id:
                print("Possibly matching sell offer to complete a trade found for the added bid...")
                possibly_matching_bids.append(bid)

        if len(possibly_matching_bids) < 1:
            # No possible trades
            # Add the sell offer to the list and return
            print("No possible trades found for the added sell offer...\nAdding sell offer to the stock trade manager.")
            self.sell_offers.append(newOffer)
            return

        # A possible trade
        # Bid order priority - Highest Price to Lowest price
        possibly_matching_bids.sort(key=lambda x: x.price, reverse=True)

        # Match the sell offer with the bid
        for possibly_matching_bid in possibly_matching_bids:
            stocks_in_bid = possibly_matching_bid.amount

            conn = sqlite3.connect('Database/Main.db')
        
            # If the sell offer has more stocks than the bid
            # aka. we overflow the bid
            if newOffer.amount > stocks_in_bid:
                print("Offer has more stocks than the bid, splitting the bid into two...")
                # We have to split the bid into two bids
                fullfilling_bid = Order(possibly_matching_bid.id,
                                          possibly_matching_bid.user,
                                          possibly_matching_bid.stock_id,
                                          newOffer.amount, possibly_matching_bid.price,
                                          possibly_matching_bid.date,
                                          1)  # Create a new bid with the remaining stocks

                remaining_bid = Order(query_next_id_for_table("bids"),
                                        possibly_matching_bid.user,
                                        possibly_matching_bid.stock_id,
                                        possibly_matching_bid.amount - newOffer.amount, # Calc the remaining stocks
                                        possibly_matching_bid.price,
                                        possibly_matching_bid.date,
                                        1)  # Create a new bid that has the remaining stocks, we need a new id for this
            
                # Remove the bid and the sell offer from the lists
                cursor = conn.execute("DELETE FROM offers WHERE id = ?", (newOffer.id, ))

                # Get the current time as the trade is happening now
                time = datetime.now()

                try:
                    conn.commit()

                    # Remove the bid
                    cursor = conn.execute("DELETE FROM bids WHERE id = ?", (fullfilling_bid.id, ))
                    conn.commit()

                    # Add trade into the database
                    cursor = conn.execute("INSERT INTO trades (buyer_user_id, seller_user_id, stock_id, amount, price, time) VALUES (?, ?, ?, ?, ?, ?)", 
                                          (str(fullfilling_bid.user.id), str(possibly_matching_bid.user.id), int(fullfilling_bid.stock_id), fullfilling_bid.amount, fullfilling_bid.price, str(time)))
                    conn.commit()

                    # Trade has been made, move the stock to the rightful owner
                    cursor = conn.execute("UPDATE user_owned_stocks SET amount = amount + ? WHERE user_id = ? AND stock_id = ?", (newOffer.amount, str(newOffer.user.id), int(newOffer.stock_id)))
                    conn.commit()

                    # Add a new bid to bids table
                    # "INSERT INTO bids (id, user_id, stock_id, amount, price, date) VALUES (1, '104294035584677999327', 1, 2, 160, '2024-03-11 19:19:54.359319');"
                    cursor = conn.execute("INSERT INTO bids (id, user_id, stock_id, amount, price, date) VALUES (?, ?, ?, ?, ?, ?)", (remaining_bid.id, str(remaining_bid.user.id), remaining_bid.stock_id, remaining_bid.amount, remaining_bid.price, str(possibly_matching_bid.date)))
                    conn.commit()

                except:
                    print("ERROR: Failed to add trade to the database!")

                finally:
                    cursor.close()
                    conn.close()

                # Add a new trade to the trades list
                self.add_trade(newOffer, fullfilling_bid, time)

                # and then add the remaining bid to the bids list
                self.add_bid(remaining_bid)

            # Sell offer has the equal or less amount of stocks than the bid
            # If the sell offer has less or equal amount of stocks than the bid
            else:
                print("Offer has equal amount of stocks or less than the bid...\nFully completing the sellers offer with the added bid.")
                conn = sqlite3.connect('Database/Main.db')
                # Remove the bid and the sell offer from the lists
                cursor = conn.execute("DELETE FROM offers WHERE id = ?", (newOffer.id, ))
                try:
                    conn.commit()

                    # Get the current time as the trade is happening now
                    time = datetime.now()

                    # Remove the bid
                    cursor = conn.execute("DELETE FROM bids WHERE id = ?", (possibly_matching_bid.id, ))
                    conn.commit()

                    # Add trade into the database
                    cursor = conn.execute("INSERT INTO trades (buyer_user_id, seller_user_id, stock_id, amount, price, time) VALUES (?, ?, ?, ?, ?, ?)", 
                                          (str(newOffer.user.id), str(possibly_matching_bid.user.id), int(newOffer.stock_id), newOffer.amount, newOffer.price, str(time), ))
                    conn.commit()

                    # Add a new trade to the trades list
                    self.add_trade(newOffer, possibly_matching_bid, time)
                except:
                    print("ERROR: Failed to add trade to the database!")
                finally:
                    cursor.close()
                    conn.close()

        self.sell_offers.append(newOffer)
        self.update()

    # Removes an old sell offer
    def remove_sell_offer(self, sell_offer_Id, userSub, stockId):
        print("Attempting to remove an sell offer from stock trade manager...")
        newSellOfferList = [sell_offer for sell_offer in self.sell_offers if not (sell_offer.id == sell_offer_Id and sell_offer.user.id == userSub and sell_offer.stock_id == stockId)]
        
        if len(newSellOfferList) == len(self.sell_offers) - 1:
            self.sell_offers = newSellOfferList
            return True
        return False

        # FIXME: Must check if this works...
        # NOTE: Remember to remove the owned stocks from the user that is selling the stocks here

    # Adds a new bid and updates
    def add_bid(self, newBid : Order):
        print("Attempting to add a new bid to stock trade manager...")
        print("Bid price: ${}".format(newBid.price))
        print("Bid amount: {} stocks".format(newBid.amount))
        print("Current stock market price: ${}".format(self.current_stock))

        # Search for possible trades (possible sell offers to match)
        # NOTE: To match the price has to be equal or lower than what we are offering in the bid
        # and the lowest price is matched first
        # if we have multiple sell offers with the same price
        # we take the oldest one first
        # you are able to only sell one or more stocks at the time
        possibly_matching_sell_offers = []
        for sell_offer in self.sell_offers:
            if newBid.price >= sell_offer.price and newBid.stock_id == sell_offer.stock_id and newBid.user.id != sell_offer.user.id:
                # Found possible trade
                print("Possibly matching sell offer to complete a trade found for the added bid...")
                possibly_matching_sell_offers.append(sell_offer)

        if len(possibly_matching_sell_offers) < 1:
            # No possible trades
            # Add the bid to the list and return
            print("No possible trades found for the added bid...\nAdding bid to the stock trade manager.")
            self.bids.append(newBid)
            return

        # We have a possible trade
        # Sort the possible sell offers by price and time
        # NOTE: We want to match the lowest sell price so we sort the prices in ascending order
        possibly_matching_sell_offers.sort(key=lambda x: (x.price, x.date)) # Sort by price and then time

        # Match the bid with the sell offer
        # NOTE: First one is the lowest price and the oldest one
        for possibly_matching_sell_offer in possibly_matching_sell_offers:
            # We now have a valid trade 
            # Check how many stocks the sell offer has
            stocks_in_sell_offer = possibly_matching_sell_offer.amount

            # NOTE: We can open a new database connection as we are going to need to change something at this point
            conn = sqlite3.connect('Database/Main.db')

            # If the sell offer has more stocks than the bid
            # aka. we overflow the sell offer
            if stocks_in_sell_offer > newBid.amount:
                print("Offer has more stocks than the bid, splitting the sell offer into two...")
                # We have to split the sell offer into two sell offers
                fullfilling_offer = Order(possibly_matching_sell_offer.id,
                                          User(possibly_matching_sell_offer.user.id),
                                          possibly_matching_sell_offer.stock_id,
                                          newBid.amount, possibly_matching_sell_offer.price,
                                          possibly_matching_sell_offer.date,
                                          1)  # Create a new sell offer with the remaining stocks

                remaining_offer = Order(query_next_id_for_table("offers"),
                                        User(possibly_matching_sell_offer.user.id),
                                        possibly_matching_sell_offer.stock_id,
                                        possibly_matching_sell_offer.amount - newBid.amount, # Calc the remaining stocks
                                        possibly_matching_sell_offer.price,
                                        possibly_matching_sell_offer.date,
                                        1)  # Create a new sell offer that has the remaining stocks, we need a new id for this

                # Remove the bid and the sell offer from the lists
                cursor = conn.execute("DELETE FROM bids WHERE id = ?", (newBid.id, ))

                # Get the current time as the trade is happening now
                time = datetime.now()

                try:
                    conn.commit()

                    
                    # Remove the sell offer
                    cursor = conn.execute("DELETE FROM offers WHERE id = ?", (fullfilling_offer.id, ))
                    conn.commit()

                    # Add trade into the database
                    cursor = conn.execute("INSERT INTO trades (buyer_user_id, seller_user_id, stock_id, amount, price, time) VALUES (?, ?, ?, ?, ?, ?)", 
                                          (str(newBid.user.id), str(possibly_matching_sell_offer.user.id), int(fullfilling_offer.stock_id), fullfilling_offer.amount, fullfilling_offer.price, str(time)))
                    conn.commit()

                    # Trade has been made, move the stock to the rightful owner
                    cursor = conn.execute("UPDATE user_owned_stocks SET amount = amount + ? WHERE user_id = ? AND stock_id = ?", (newBid.amount, str(newBid.user.id), int(newBid.stock_id)))
                    conn.commit()

                    # Add a new offer to offers table
                    # "INSERT INTO offers (id, user_id, stock_id, amount, price, date) VALUES (1, '104294035584677999327', 1, 2, 160, '2024-03-11 19:19:54.359319');"
                    cursor = conn.execute("INSERT INTO offers (id, user_id, stock_id, amount, price, date) VALUES (?, ?, ?, ?, ?, ?)", (remaining_offer.id, str(remaining_offer.user.id), remaining_offer.stock_id, remaining_offer.amount, remaining_offer.price, str(possibly_matching_sell_offer.date)))
                    conn.commit()

                except:
                    print("ERROR: Failed to add trade to the database!")

                finally:
                    cursor.close()
                    conn.close()

                # Add a new trade to the trades list
                self.add_trade(newBid, fullfilling_offer, time)

                # and then add the remaining stock offer to the sell offers list
                self.add_offer(remaining_offer)  # NOTE: this will try to match the remaining stocks with a matching bid

            # Sell offer has the equal or less amount of stocks than the bid
            # If the sell offer has less or equal amount of stocks than the bid
            else:
                print("Offer has equal amount of stocks or less than the bid...\nFully completing the sellers offer with the added bid.")
                conn = sqlite3.connect('Database/Main.db')
                # Remove the bid and the sell offer from the lists
                cursor = conn.execute("DELETE FROM bids WHERE id = ?", (newBid.id, ))
                try:
                    conn.commit()

                    # Get the current time as the trade is happening now
                    time = datetime.now()

                    # Remove the sell offer
                    cursor = conn.execute("DELETE FROM offers WHERE id = ?", (possibly_matching_sell_offer.id, ))
                    conn.commit()

                    # Add trade into the database
                    cursor = conn.execute("INSERT INTO trades (buyer_user_id, seller_user_id, stock_id, amount, price, time) VALUES (?, ?, ?, ?, ?, ?)", 
                                          (str(newBid.user.id), str(possibly_matching_sell_offer.user.id), int(newBid.stock_id), newBid.amount, newBid.price, str(time), ))
                    conn.commit()

                    # Add a new trade to the trades list
                    self.add_trade(newBid, possibly_matching_sell_offer, time)
                except:
                    print("ERROR: Failed to add trade to the database!")
                finally:
                    cursor.close()
                    conn.close()

        self.bids.append(newBid)
        self.update()

    # Removes an old bid
    def remove_bid(self, bidId, userSub, stockId):
        print("Attempting to remove an bid from stock trade manager...")
        newBidList = [bid for bid in self.bids if not (bid.id == bidId and bid.user.id == userSub and bid.stock_id == str(stockId))]
        
        if len(newBidList) == len(self.bids) - 1:
            self.bids = newBidList
            return True
        return False

    # General update that is used whenever a new stock price is fetched 
    # and when bids or sell offers are added 
    # This will update the whole system and match bids with sell offers if possible
    # based on the newest stock market price
    # TODO: We should have a parameter that indicates if the update is done after
    # a stock market price change
    # as if this happens, we might have bids and sell offers that are outside of the ±10% price deviation
    def update(self):
        # TODO: implement this
        if (False):
            for bid in self.bids:
                for sell_offer in self.sell_offers:
                    # Early exit if the bid and sell offer user_id is the same (user would be buying from themselves)
                    if sell_offer.user_id == bid.user_id:
                        continue

                    # TODO: (Pate 󰯈 ) Check against the market price that this is not more than ±10% of the market price
                    # Match the bid with the sell offer

                    # If the bid price is greater than or equal to the sell offer price
                    # we have a valid trade
                    if bid.price >= sell_offer.price:
                        # TODO: (Pate 󰯈 ) We should split the sell offer if the amount is greater than the bid amount here

                        # NOTE: We have a chance to duplicate a stock here if the server would crash during this
                        # TODO: Make this transactional
                        conn = sqlite3.connect('Database/Main.db')
                        # Remove the bid and the sell offer from the lists
                        # cursor = conn.execute("DELETE FROM bids WHERE id = ?", (bid.id))
                        cursor = conn.execute("DELETE FROM bids WHERE id = ?", (bid.id, ))
                        try:
                            conn.commit()
                        except:
                            pass

                        finally:
                            cursor.close()
                            conn.close()

                        # Get time for the trade
                        time = datetime.now()

                        self.add_trade(bid, sell_offer, time)

                        # Add a new trade to the trades list
                        # TODO: We should split the sell offer if the amount is greater than the bid amount

                        # conn.commit()
