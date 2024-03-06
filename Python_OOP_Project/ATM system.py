from abc import ABC, abstractmethod
import datetime
import os
from enum import Enum
import uuid


class Bank:
    def __init__(self, name, bank_swift_code):
        self.name = name
        self.bank_swift_code = bank_swift_code
        self.customers = []
        
    def add_customer(self, customer):
        self.customers.append(customer)
    
    def get_account(self, account_number):
        for customer in self.customers:
            for account in customer.accounts:
                if account.account_number == account_number:
                    return account
        return None

class Authenticator:
    def __init__(self, bank):
        self.bank = bank
        
    def authenticate(self, card_number, pin):
        for customer in self.bank.customers:
            for account in customer.accounts:
                if account.linked_card.card_number == card_number:
                    if account.linked_card.get_pin() == pin:
                        return account
        return None

class screen:
    def display_message(self, message):
        print(message)
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

class Keypad:
    def get_input(self, message):
        return input(message)

class ATM:
    def __init__(self, atm_location, bank):
        self.atm_location = atm_location
        self.bank = bank
        self.screen = screen()
        self.keypad = Keypad()
        self.card_reader = CardReader(self, bank)
    
    
        
    def display_main_menu(self, account):
        message = """
ATM Menu
1. Check balance
2. Deposit
3. Withdraw
4. Transfer
5. View transactions
6. Change pin
7. Quit
Choose an option: """
        while True:
            choice = self.keypad.get_input(message)
            if choice == '7':
                self.screen.clear_screen()
                print('Thank you for using the ATM')
                break
            self.handle_menu_selection(choice, account)
    
    def handle_menu_selection(self, choice, account):
            match choice:
                case '1':
                    self.screen.clear_screen()
                    account.check_balance()
                case '2':
                    self.screen.clear_screen()
                    self.deposit(account)
                case '3':
                    self.screen.clear_screen()
                    self.withdraw(account)
                case '4':
                    self.screen.clear_screen()
                    self.transfer(account)
                case '5':
                    self.screen.clear_screen()
                    self.view_transactions(account)
                case "6":
                    self.screen.clear_screen()
                    self.change_pin(account.linked_card)
                case _:
                    if choice.isnumeric():
                        self.screen.clear_screen()
                        self.screen.display_message('Invalid option')
                    else:
                        self.screen.clear_screen()
                        self.screen.display_message('Invalid input')
        
    def withdraw(self, account):
        amount = float(self.keypad.get_input('Enter amount to withdraw: '))
        if amount > 0:
            withdraw = WithdrawTransaction(amount)
            withdraw.execute(account)
        else:
            self.screen.display_message('Invalid amount')
    
    def deposit(self, account):
        amount = float(self.keypad.get_input('Enter amount to deposit: '))
        if amount > 0:
            deposit = DepositTransaction(amount)
            deposit.execute(account)
        else:
            self.screen.display_message('Invalid amount')
    
    def view_transactions(self, account):
        for transaction in account.transaction_history:
            self.screen.display_message(transaction)
    
    def transfer(self, account):
        recipient_account_number = self.keypad.get_input('Enter recipient account number: ')
        recipient = self.bank.get_account(recipient_account_number)
        if recipient:
            amount = float(self.keypad.get_input('Enter amount to transfer: '))
            if amount > 0:
                transfer = TransferTransaction(amount, recipient)
                transfer.execute(account)
            else:
                self.screen.display_message('Invalid amount')
        else:
            self.screen.display_message('Recipient account not found')
    
    def change_pin(self, card):
        old_pin = self.keypad.get_input('Enter old pin: ')
        new_pin = self.keypad.get_input('Enter new pin: ')
        card.set_pin(old_pin, new_pin)

class CardReader:
    def __init__(self, atm, bank):
        self.authenticator = Authenticator(bank)
        self.atm = atm
        self.screen = screen()
        self.keypad = Keypad()
        self.bank = bank
        self.atm = atm
        self.authenticator = Authenticator(bank)
    
        
    def insert_card(self, card):
        
        while True:
            pin = self.keypad.get_input('Please enter your pin: ')
            account = self.authenticator.authenticate(card.get_card_number(), pin)
            if account:
                self.keypad.get_input('Card accepted. Press enter to continue')
                self.screen.clear_screen()
                self.atm.display_main_menu(account)
                break
            else:
                self.screen.clear_screen()
                self.screen.display_message('Invalid card or pin')

class Customer:
    def __init__(self, name, address, phone_number, email):
        self.name = name
        self.address = address
        self.phone_number = phone_number
        self.email = email
        self.accounts = []
    
    def __repr__(self):
        return f'Customer: {self.name}'
    
    def add_account(self, account):
        self.accounts.append(account)

class Account:
    def __init__(self, account_number):
        self.account_number = account_number
        self.balance = 0
        self.linked_card = None
        self.transaction_history = []
    
    def __repr__(self):
        return f'Account No.{self.account_number}'
    
    def add_transaction(self, transaction):
        self.transaction_history.append(transaction)
        
    def link_card(self, card):
        self.linked_card = card
    
    def check_balance(self):
        print(f'Your balance is ${self.balance}')

class Card:
    def __init__(self, card_number, pin):
        self.card_number = card_number
        self.__pin = pin
        self.screen = screen()
        self.keypad = Keypad()
    
    def __repr__(self):
        return f'Card number: {self.card_number}'
    
    def get_pin(self):
        return self.__pin
    
    def set_pin(self, old_pin, new_pin):
        if old_pin == self.__pin:
            self.__pin = new_pin
            self.screen.display_message('Pin changed successfully')
        else:
            self.screen.display_message('Invalid pin')
        
    def get_card_number(self):
        return self.card_number

class Transaction(ABC):
    
    def __repr__(self):
        return f'(ID: {self.transaction_id} - Type: {self.transaction_type} - Amount: {self.amount} - Timestamp: {self.timestamp})'
    
    def __init__(self, transaction_type, amount=None):
        self.transaction_id = uuid.uuid4()
        self.timestamp = datetime.datetime.now()
        self.transaction_type = transaction_type
        self.amount = amount
    
    @abstractmethod
    def execute(self):
        pass

class TransactionType(Enum):
    DEPOSIT = 'Deposit'
    WITHDRAW = 'Withdraw'
    BALANCE_INQUIRY = 'Balance Inquiry'
    TRANSFER = 'Transfer'

class WithdrawTransaction(Transaction):
    def __init__(self, amount):
        super().__init__(TransactionType.WITHDRAW.name, amount)
        self.amount = amount
    
    def execute(self, account):
        if account.balance >= self.amount:
            account.balance -= self.amount
            account.add_transaction(self)
            print(f'Withdrawal of ${self.amount} successful. New balance is ${account.balance}')
        else:
            print('Insufficient funds')
            
class DepositTransaction(Transaction):
    def __init__(self, amount):
        super().__init__(TransactionType.DEPOSIT.name, amount)
        self.amount = amount
        
    def execute(self, account):
            account.balance += self.amount
            account.add_transaction(self)
            print(f'Deposit of ${self.amount} successful. New balance is ${account.balance}')

class TransferTransaction(Transaction):
    def __init__(self, amount, recipient):
        super().__init__(TransactionType.TRANSFER.name, amount)
        self.amount = amount
        self.recipient = recipient
    
    def execute(self, account):
        if account.balance >= self.amount:
            account.balance -= self.amount
            account.add_transaction(self)
            self.recipient.balance += self.amount
            self.recipient.add_transaction(self)
            print(f'Transfer of ${self.amount} successful. New balance is ${account.balance}')
        else:
            print('Insufficient funds')

class BalanceInquiryTransaction(Transaction):  # balance inquiry = checking the balance = الاستفسار عن الرصيد
    def __init__(self):
        super().__init__(TransactionType.BALANCE_INQUIRY.name)
    
    def __repr__(self):
        return f'(ID: {self.transaction_id} - Type: {self.transaction_type} - Timestamp: {self.timestamp})'
    
    def execute(self, account):
        print(f'Your balance is ${account.balance}')
        account.add_transaction(self)


Alahly_bank = Bank('Alahly', 'ALAHLY123')
moaz = Customer('moaz', 'cairo', '01111111111', 'moazmo@gmail.com')
account1 = Account('123456789')
card1 = Card('123456789', '1234')

hagar = Customer("hagar", "cairo", "022222", "hagar@gmail.com")
account2 = Account("987654321")
card2 = Card("987654321", "4321")

Alahly_bank.add_customer(moaz)
moaz.add_account(account1)
account1.link_card(card1)

Alahly_bank.add_customer(hagar)
hagar.add_account(account2)
account2.link_card(card2)

DepositTransaction(100).execute(account1)
DepositTransaction(100).execute(account1)
BalanceInquiryTransaction().execute(account1)

print(account1.transaction_history)

Alahly_bank_atm = ATM('cairo', Alahly_bank)
Alahly_bank_atm.card_reader.insert_card(card1)

account2.check_balance()