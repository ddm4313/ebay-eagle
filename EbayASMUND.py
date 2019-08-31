from ebaysdk.trading import Connection
import json, xmltodict
from collections import OrderedDict
# I will release this in the future as a module once I make sure every important function is included and it's stable.

class TheEbayAsmund:
    def connect_and_execute(self):
        ''''''
        self.api = Connection(config_file='ebay.yaml', domain='api.sandbox.ebay.com', debug=False)
    def xmltojson(self, function):
        self.output_dict = json.loads(json.dumps(xmltodict.parse(function)))
    def list(self):
        """
            CREATE AN EBAY LISTING
            """
        self.connect_and_execute()
        self.item_info = open("item_info.json", "r")
        self.item_info = json.load(self.item_info)
        self.item_title = self.item_info['item_name']
        self.location = self.item_info['location']
        self.site = self.item_info['Site']
        self.PayPal_EMAIL = self.item_info['PayPal_EMAIL']
        self.description = self.item_info['Description']
        self.return_description = self.item_info['ReturnDescription']
        self.handling_time = self.item_info['Description']
        self.Price = self.item_info['Price']

        self.request = {
            "Item": {
                "Title": self.item_title,
                "Country": "US",
                "Location": self.location,
                "Site": "US",
                "ConditionID": "1000",
                "PaymentMethods": "PayPal",
                "PayPalEmailAddress": self.PayPal_EMAIL,
                "PrimaryCategory": {"CategoryID": "33963"},
                "Description": self.description,
                "ListingDuration": "GTC",
                "StartPrice": self.price,
                "Currency": "USD",
                "ReturnPolicy": {
                    "ReturnsAcceptedOption": "ReturnsAccepted",
                    "RefundOption": "MoneyBack",
                    "ReturnsWithinOption": "Days_30",
                    "Description": self.return_description,
                    "ShippingCostPaidByOption": "Buyer"
                },
                "ShippingDetails": {
                    "ShippingServiceOptions": {
                        "FreeShipping": "True",
                        "ShippingService": "USPSMedia" # you can put others aswell, such as FedEx Home Delivery/Smart Post, etc.
                    }
                },
                "DispatchTimeMax": self.handling_time
            }
        }
    def gather_info(self):
        '''GATHER INFO ABOUT THE SELLER & THE USER'''
        self.connect_and_execute()
        self.api.execute("GetSellerTransactions")
        self.seller_transactions = self.api.response_content()
        self.xmltojson(function=self.seller_transactions)
        #["Buyer"]["Email"]
        self.seller_id = self.output_dict['GetSellerTransactionsResponse']['Seller']['UserID']
        self.buyer_mail = self.output_dict["GetSellerTransactionsResponse"]['TransactionArray']['Transaction'][0]['Buyer']['Email']
        self.buyer_feedback = self.output_dict["GetSellerTransactionsResponse"]['TransactionArray']['Transaction'][0]['Buyer']['FeedbackScore']
        self.buyer_id = self.output_dict["GetSellerTransactionsResponse"]['TransactionArray']['Transaction'][0]['Buyer']['UserID']
        self.buyer_country = self.output_dict["GetSellerTransactionsResponse"]['TransactionArray']['Transaction'][0]['Buyer']['BuyerInfo']['ShippingAddress']['CountryName']
        self.item_id = self.output_dict["GetSellerTransactionsResponse"]['TransactionArray']['Transaction'][0]['Item']['ItemID']
        self.transaction_id = self.output_dict["GetSellerTransactionsResponse"]['TransactionArray']['Transaction'][0]['TransactionID']
        self.quantity = self.output_dict["GetSellerTransactionsResponse"]['TransactionArray']['Transaction'][0]['Item']['Quantity']
        self.price = self.output_dict["GetSellerTransactionsResponse"]['TransactionArray']['Transaction'][0]['Item']['SellingStatus']['CurrentPrice']['#text']
        print(f"Buyer ID: {self.buyer_id} | Buyer Email: {self.buyer_mail} | Buyer Feedback: {self.buyer_feedback} | Country: {self.buyer_country} | Item ID: {self.item_id} | Quantity: {self.quantity} | Transaction ID: {self.transaction_id} | Price: $%s" % self.price)
    def send_message(self):
        try:
            self.gather_info()
            self.api.execute('AddMemberMessageAAQToPartner', {"ItemID": self.item_id, "MemberMessage": {"Body": "test",
                                                                                                        "RecipientID": self.buyer_id,
                                                                                                        "Subject": "No man, you are bad fsafsaafsfsafsafsa.",
                                                                                                        "Question": "You're befasfsafsaafssst",
                                                                                                        "QuestionType": "General"}})
            self.message_response = self.api.response_content()
            self.xmltojson(function=self.message_response)
        except:
            print("EBAY SERVER ERROR [FAILED TO SEND MESSAGE]: Code 10007")
    def completesale(self):
        self.gather_info()
        self.api.execute('CompleteSale', {"ItemID": self.item_id, "TransactionID": self.transaction_id, "Shipped": True}).text
        self.completesale_info = self.api.response_content()
        self.xmltojson(function=self.completesale_info)
        if self.output_dict["CompleteSaleResponse"]["Ack"] == "Success":
            print("EBAY RESPONSE: Marked shipment as sent.")
    def getaccount(self):
        '''
        GETS DATA FROM THE SELLER DASHBOARD SUCH AS POWER STATUS LEVEL WILL ADD MORE SOON
        :return:
        '''
        self.gather_info()
        self.api.execute('GetSellerDashboard')
        self.xmltojson(self.api.response_content())
        self.SellerDashboard = self.output_dict["GetSellerDashboardResponse"]
        if self.output_dict["GetSellerDashboardResponse"]["Ack"] == "Success":
            print(f"User ID: {self.seller_id} | Power Level Status: {self.SellerDashboard['PowerSellerStatus']['Level']}")
Ebay = TheEbayAsmund()
Ebay.getaccount()
