

# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

#LIST_CATEGORIES = {"Phone":"Phone", "Calling Device":"Phone", "Tablet":"Tablet", "iPad":"Tablet", "pc":"Computer", "Computer":"Computer"}
#LIST_BRANDS = ["Hewlett-Packard (HP)", "Lenovo" , "Acer" , "Asus" , "Apple" , "Microsoft" , "MSI" , "Samsung" , "Xiaomi" , "Huawei" , "Razer"]

#PATH_FILE_PRODUCTS = "persistence\products.json"
#PATH_FILE_USERS = "persistence\users.json"
#PATH_FILE_BRANDS = "persistence\brands.json"
#PATH_FILE_CATEGORIES = "persistence\categories.json"
FILE = "persistence\data.json"

from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import AllSlotsReset, SlotSet, ActiveLoop
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from collections import OrderedDict
from os import path

import json
import re

def userDataValidation(input, format):
    #'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
    #'3+[0-9]+'
    regex = re.compile(format)
    if re.fullmatch(regex, input):
      return True
    else:
      return False
#VIEW ACTION
         
class showCategoryList(Action):
    def name(self) -> Text:
        return "show_category_list"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        output = "Categories for sale"
        with open(FILE) as file:
            data = json.load(file)
        for x in data["list_categories"]:
            output+= "\n    - " + x
        output += "\n- Choose one\n- Back"
        dispatcher.utter_message(text =output)

class showBrandList(Action):
    def name(self) -> Text:
        return "show_brand_list"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        output = "Brand for sale:" 
        with open(FILE) as file:
            data = json.load(file)
        for brand in data["list_brands"]:
            output+= ("\n    - " + brand)
        output += "\n- Choose one\n- Back"
        dispatcher.utter_message(text =output)

class showAllProductsList(Action):
    def name(self) -> Text:
        return "show_all_product_list"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if (len(tracker.latest_message['entities'])==0):
            dispatcher.utter_message("Result not found" )
        else:
            entity_name = tracker.latest_message['entities'][0]['entity']
            entity_value = tracker.latest_message['entities'][0]['group']
            if path.isfile(FILE):
                with open(FILE) as file:
                    products = json.load(file)['products']
                products = list(filter(lambda x: (x[entity_name]==entity_value and x['seller']==x['owner']), products))
                output = entity_name+ " "+entity_value + " for sale:" 
                if len(products) > 0:
                    for x in products:
                        output+= ("\n- ID product: "+ x['id'])
                        output+= ("\n     - Model: " + x['model'])
                        output+= ("\n     - Category: " + x['category'])
                        output+= ("\n     - Brand: " + x['brand'])
                        output+= ("\n     - Price: " + str(x['price']))
                        output+= ("\n     - Seller: " + x['seller'])
                else:
                    output+="\n None"
                dispatcher.utter_message(text = output )
            else:
                dispatcher.utter_message(text = entity_name+ " not found" )

#HISTORY FORM

class validateAuthForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_auth_form"
    def validate_email(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
        if tracker.latest_message['intent']['name'] == "reset":
            return {'requested_slot':None}
        else:
            regex = re.compile('([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
            if re.fullmatch(regex, slot_value):
                return {"email":slot_value} 
            else:
                return {"email":None}
    
    def validate_confirm_auth(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
        answer = tracker.latest_message['intent']['name']
        if answer == "reset":
            return {'requested_slot':None}
        elif answer == "affirm":
            return {"confirm_auth":"yes"} 
        elif answer == "deny":
            return {"confirm_auth":"no"}  
        else:
            return {"confirm_auth":None}

class showOwnProductsList(Action):
    def name(self) -> Text:
        return "show_own_product_list"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("confirm_auth") == "yes":
            if path.isfile(FILE):
                with open(FILE) as file:
                    data = json.load(file)
                user_email = tracker.get_slot("email")
                
                if (user_email in data["users"]):
                    bought_products = list(filter(lambda x: (x['owner']==user_email and x['seller']!=user_email), data['products']))
                    sold_products = list(filter(lambda x: (x['seller']==user_email and x['owner']!=user_email), data['products']))
                    pending_products = list(filter(lambda x: (x['owner']==user_email and x['seller']==user_email), data['products']))
                    output = "You product history:"
                    
                    output+="\n\nProducts bought:"
                    if len(bought_products)>0:
                        for x in bought_products:
                            output+= ("\n- ID product: "+ x['id'])
                            output+= ("\n    - Model: " + x['model'])
                            output+= ("\n    - Category: " + x['category'])
                            output+= ("\n    - Brand: " + x['brand'])
                            output+= ("\n    - Price: " + str(x['price']))
                            output+= ("\n    - Seller: " + x['seller'])
                    else:
                        output+="\n None"

                    output+="\n\nProducts sold:"
                    if len(sold_products)>0:
                        for x in sold_products:
                            output+= ("\n- ID product: "+ x['id'])
                            output+= ("\n    - Model: " + x['model'])
                            output+= ("\n    - Category: " + x['category'])
                            output+= ("\n    - Brand: " + x['brand'])
                            output+= ("\n    - Price: " + str(x['price']))
                            output+= ("\n    - Buyer: " + x['owner'])
                    else:
                        output+="\n None"
            
                    output+="\n\nProducts pending:"
                    if len(pending_products)>0:
                        for x in pending_products:
                            output+= ("\n- ID product: "+ x['id'])
                            output+= ("\n    - Model: " + x['model'])
                            output+= ("\n    - Category: " + x['category'])
                            output+= ("\n    - Brand: " + x['brand'])
                            output+= ("\n    - Price: " + str(x['price']))
                    else:
                        output+="\n None"

                    dispatcher.utter_message(text = output )
                else:
                    dispatcher.utter_message(text = "No users associated with the e-mail" )
            else: 
                dispatcher.utter_message(text = "Error" )
        else:
            dispatcher.utter_message(text =  "Cancelled authentication" )
            return[AllSlotsReset()]


#PURCHASE FORM

class validatePurchaseForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_purchase_form"

    def validate_product_id(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
        if tracker.latest_message['intent']['name'] == "reset":
            return {'requested_slot':None}
        else:    
            if path.isfile(FILE):
                with open(FILE) as file:
                    products = json.load(file)['products']
                products = list(map(lambda x: (x['id']), products))
                result = list(filter(lambda x: (x.lower() == slot_value.lower()), products))
                if len(result) == 0:
                    return {"product_id":None} 
                else:
                    return {"product_id":result[0]}
            else:
                return {'requested_slot':None}

    def validate_email(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
        if tracker.latest_message['intent']['name'] == "reset":
            return {'requested_slot':None}
        else:
            regex = re.compile('([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
            if re.fullmatch(regex, slot_value):
                return {"email":slot_value} 
            else:
                return {"email":None}

    def validate_confirm_purchase(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
        answer = tracker.latest_message['intent']['name']
        if answer == "reset":
            return {'requested_slot':None}
        elif answer == "affirm":
            return {"confirm_purchase":"yes"} 
        elif answer == "deny":
            return {"confirm_purchase":"no"}  
        else:
            return {"confirm_purchase":None}

class actionSavePurchase(Action):

    def name(self) -> Text:
        return "action_save_purchase"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("confirm_purchase") == "yes":
            product = tracker.get_slot("product_id")
            email = tracker.get_slot("email")
            if path.isfile(FILE):

                with open(FILE) as file:
                    data = json.load(file)
                products = data['products']
                users = data['users']
                list_id = list(map(lambda x: (x['id']), products))
                index = list_id.index(product)
                if not(products[index]["owner"] == products[index]["seller"]):
                    dispatcher.utter_message(text = product + " not for sale")
                else:
                    if email not in users:
                        users.append(email)
                    products[index]["owner"] = email
                    data['products']=products
                    data['users']=users
                    with open(FILE, 'w') as outfile:
                        json.dump(data, outfile, indent=2)
                    dispatcher.utter_message(text = "Registered order")
            else:
                dispatcher.utter_message(text = "Error")
            return[AllSlotsReset()]
        else:
            dispatcher.utter_message(text =  "Cancelled order" )
            return [AllSlotsReset()]

class validateSellingForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_selling_form"

    def validate_category(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
        if tracker.latest_message['intent']['name'] == "reset":
            return {'requested_slot':None}
        elif len(tracker.latest_message['entities'])==0:
            return {"category":None}
        elif tracker.latest_message['entities'][0]['entity'] == 'category':
            tracker.latest_message['entities'][0]['group']
            return {"category":tracker.latest_message['entities'][0]['group']} 
        else:
            return {"category":None}


    def validate_brand(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
        if tracker.latest_message['intent']['name'] == "reset":
            return {'requested_slot':None}
        elif len(tracker.latest_message['entities'])==0:
            return {"brand":None}
        elif tracker.latest_message['entities'][0]['entity'] == 'brand':
            return {"brand":tracker.latest_message['entities'][0]['group']} 
        else:
            return {"category":None}


    def validate_product_model(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
        if tracker.latest_message['intent']['name'] == "reset":
            return [ActiveLoop(None), SlotSet('requested_slot',None)]
        else:
            if len(slot_value) == 0:
                return {"product_model":None} 
            else:
                return {"product_model":slot_value}
        

    def validate_price(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
        if tracker.latest_message['intent']['name'] == "reset":
            return {'requested_slot':None}
        else:
            regex = re.compile('[0-9]+')
            if re.fullmatch(regex, slot_value):
                return {"price":slot_value} 
            else:
                return {"price":None}
    

    def validate_email(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
        if tracker.latest_message['intent']['name'] == "reset":
            return {'requested_slot':None}
        else:
            regex = re.compile('([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
            if re.fullmatch(regex, slot_value):
                return {"email":slot_value} 
            else:
                return {"email":None}
    
    def validate_confirm_selling(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
        answer = tracker.latest_message['intent']['name']
        if answer == "reset":
            return {"confirm_selling":None} 
        elif answer == "affirm":
            return {"confirm_selling":"yes"} 
        elif answer == "deny":
            return {"confirm_selling":"no"}  
        else:
            return {"confirm_selling":None}

class actionSaveSelling(Action):

    def name(self) -> Text:
        return "action_save_selling"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("confirm_selling") == "yes":
            product = tracker.get_slot("product_model")
            category = tracker.get_slot("category")
            brand = tracker.get_slot("brand")
            price = tracker.get_slot("price")
            email = tracker.get_slot("email")
            if path.isfile(FILE):

                with open(FILE) as file:
                    data = json.load(file)
                products = data['products']
                users = data['users']
                products_ = list(filter(lambda x: (x['brand'] == brand and x['category'] == category), products))
                products_ = list(map(lambda x: (x['id']), products_))
                products_ = list(map(lambda x: ([int(s) for s in re.findall(r'-?\d+\.?\d*', x)]), products_))
                if len(products_)==0:
                    id = category[0]+brand[slice(0, 2)]+"0"
                else:   
                    id = category[0]+brand[slice(0, 2)]+str(max(products_)[0]+1 )
                if email not in users:
                    users.append(email)

            else:
                id = category[0]+brand[slice(0, 2)]+"0"
                products = []
                users = [email]
            # %s"%(u"\N{euro sign}")
            products.append({
                    "model": product,
                    "id":id,
                    "category": category,
                    "brand": brand,
                    "price": price,
                    "seller": email,
                    "owner": email
                })
            data['products']=products
            data['users']=users
            with open(FILE, 'w') as outfile:
                json.dump(data, outfile, indent=2)

            dispatcher.utter_message(text =  "Registered selling")
            return[AllSlotsReset()]
        else:
            dispatcher.utter_message(text =  "Cancelled selling" )
            return [AllSlotsReset()]

#--------

class actionSlotReset(Action):
    def name(self) -> Text:
        return "action_slot_reset"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [AllSlotsReset()]
        
        



            
        
