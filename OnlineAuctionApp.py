from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Union
import uuid

class AuctionStatus(Enum):
    UPCOMING = "upcoming"
    LIVE = "live"
    ENDED = "ended"
    CANCELLED = "cancelled"


class BidStatus(Enum):
    ACTIVE = "active"
    WINNING = "winning"
    OUTBID = "outbid"
    WON = "won"
    LOST = "lost"


class NotificationType(Enum):
    AUCTION_START = "auction_start"
    AUCTION_END = "auction_end"
    NEW_BID = "new_bid"
    OUTBID = "outbid"
    WINNING_BID = "winning_bid"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"


class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class BaseModel:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def update(self):
        self.updated_at = datetime.now()

class User(BaseModel):
    def __init__(self, username: str, email: str, password: str):
        super().__init__()
        self.username = username
        self.email = email
        self._password = password
        self.is_active = True
        self.rating = 0.0
        self.auctions_participated = []
        self.auctions_created = []
        self.watchlist = []
        self.payment_methods = []

    def add_payment_method(self, payment_method):
        self.payment_methods.append(payment_method)
        self.update()

    def update_profile(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)
        self.update()

class UserRepository:
    def __init__(self):
        self.users = {}  # user_id -> User

    def create(self, username: str, email: str, password: str) -> User:
        user = User(username, email, password)
        self.users[user.id] = user
        return user

    def get(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    def update(self, user: User) -> User:
        if user.id in self.users:
            self.users[user.id] = user
            user.update()
        return user

    def delete(self, user_id: str) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False

class Category(BaseModel):
    def __init__(self, name: str, description: str = ""):
        super().__init__()
        self.name = name
        self.description = description
        self.parent_id = None
        self.subcategories = []

    def add_subcategory(self, subcategory):
        subcategory.parent_id = self.id
        self.subcategories.append(subcategory.id)
        self.update()

class Item(BaseModel):
    def __init__(self, name: str, description: str, category_id: str, seller_id: str):
        super().__init__()
        self.name = name
        self.description = description
        self.category_id = category_id
        self.seller_id = seller_id
        self.images = []
        self.condition = "New"
        self.tags = []

    def add_image(self, image_url: str):
        self.images.append(image_url)
        self.update()

    def set_condition(self, condition: str):
        self.condition = condition
        self.update()

    def add_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)
            self.update()

class ItemRepository:
    def __init__(self):
        self.items = {}  # item_id -> Item

    def create(self, name: str, description: str, category_id: str, seller_id: str) -> Item:
        item = Item(name, description, category_id, seller_id)
        self.items[item.id] = item
        return item

    def get(self, item_id: str) -> Optional[Item]:
        return self.items.get(item_id)

    def update(self, item: Item) -> Item:
        if item.id in self.items:
            self.items[item.id] = item
            item.update()
        return item

    def delete(self, item_id: str) -> bool:
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False

    def search(self, query: str, category_id: Optional[str] = None) -> List[Item]:
        results = []
        for item in self.items.values():
            if (query.lower() in item.name.lower() or 
                query.lower() in item.description.lower() or
                query.lower() in item.tags):
                if category_id is None or item.category_id == category_id:
                    results.append(item)
        return results

class Auction(BaseModel):
    def __init__(self, item_id: str, seller_id: str, start_price: float, 
                 start_time: datetime, end_time: datetime):
        super().__init__()
        self.item_id = item_id
        self.seller_id = seller_id
        self.start_price = start_price
        self.current_price = start_price
        self.reserve_price = None
        self.start_time = start_time
        self.end_time = end_time
        self.status = AuctionStatus.UPCOMING
        self.bids = []
        self.current_winner_id = None
        self.auto_extend = True 
        self.extension_minutes = 5
        self.extension_threshold_minutes = 2

    def place_bid(self, bid):
        if self.status != AuctionStatus.LIVE:
            raise ValueError(f"Cannot place bid on auction with status: {self.status}")
            
        if bid.amount <= self.current_price:
            raise ValueError(f"Bid amount ({bid.amount}) must be greater than current price ({self.current_price})")
            
        for existing_bid in self.bids:
            if existing_bid.bidder_id == bid.bidder_id and existing_bid.status == BidStatus.ACTIVE:
                existing_bid.status = BidStatus.OUTBID
                
        if self.current_winner_id:
            for existing_bid in self.bids:
                if existing_bid.bidder_id == self.current_winner_id and existing_bid.status == BidStatus.WINNING:
                    existing_bid.status = BidStatus.OUTBID
        
        bid.status = BidStatus.WINNING
        self.bids.append(bid)
        self.current_price = bid.amount
        self.current_winner_id = bid.bidder_id
        
        if self.auto_extend and self.should_extend():
            self.extend_auction()
            
        self.update()
        return bid

    def should_extend(self) -> bool:
        now = datetime.now()
        time_remaining = (self.end_time - now).total_seconds() / 60
        return time_remaining <= self.extension_threshold_minutes

    def extend_auction(self):
        self.end_time = self.end_time.replace(
            minute=self.end_time.minute + self.extension_minutes
        )

    def start_auction(self):
        if self.status != AuctionStatus.UPCOMING:
            raise ValueError(f"Cannot start auction with status: {self.status}")
        self.status = AuctionStatus.LIVE
        self.update()

    def end_auction(self):
        if self.status != AuctionStatus.LIVE:
            raise ValueError(f"Cannot end auction with status: {self.status}")
            
        self.status = AuctionStatus.ENDED
        
        for bid in self.bids:
            if bid.bidder_id == self.current_winner_id and bid.status == BidStatus.WINNING:
                bid.status = BidStatus.WON
            elif bid.status in [BidStatus.ACTIVE, BidStatus.OUTBID]:
                bid.status = BidStatus.LOST
        
        self.update()

    def cancel_auction(self):
        if self.status == AuctionStatus.ENDED:
            raise ValueError("Cannot cancel an auction that has already ended")
            
        self.status = AuctionStatus.CANCELLED
        self.update()


class Bid(BaseModel):
    def __init__(self, auction_id: str, bidder_id: str, amount: float):
        super().__init__()
        self.auction_id = auction_id
        self.bidder_id = bidder_id
        self.amount = amount
        self.status = BidStatus.ACTIVE
        self.auto_bid = False
        self.max_bid_amount = None

    def set_auto_bid(self, max_amount: float):
        self.auto_bid = True
        self.max_bid_amount = max_amount
        self.update()


class AuctionRepository:
    def __init__(self):
        self.auctions = {}

    def create(self, item_id: str, seller_id: str, start_price: float, 
               start_time: datetime, end_time: datetime) -> Auction:
        auction = Auction(item_id, seller_id, start_price, start_time, end_time)
        self.auctions[auction.id] = auction
        return auction

    def get(self, auction_id: str) -> Optional[Auction]:
        return self.auctions.get(auction_id)

    def update(self, auction: Auction) -> Auction:
        if auction.id in self.auctions:
            self.auctions[auction.id] = auction
            auction.update()
        return auction

    def delete(self, auction_id: str) -> bool:
        if auction_id in self.auctions:
            del self.auctions[auction_id]
            return True
        return False

    def get_active_auctions(self) -> List[Auction]:
        now = datetime.now()
        return [
            auction for auction in self.auctions.values() 
            if auction.status == AuctionStatus.LIVE and auction.end_time > now
        ]

    def get_upcoming_auctions(self) -> List[Auction]:
        return [
            auction for auction in self.auctions.values() 
            if auction.status == AuctionStatus.UPCOMING
        ]

    def get_ended_auctions(self) -> List[Auction]:
        return [
            auction for auction in self.auctions.values() 
            if auction.status == AuctionStatus.ENDED
        ]


class BidRepository:
    def __init__(self):
        self.bids = {}

    def create(self, auction_id: str, bidder_id: str, amount: float) -> Bid:
        bid = Bid(auction_id, bidder_id, amount)
        self.bids[bid.id] = bid
        return bid

    def get(self, bid_id: str) -> Optional[Bid]:
        return self.bids.get(bid_id)

    def get_by_auction(self, auction_id: str) -> List[Bid]:
        return [bid for bid in self.bids.values() if bid.auction_id == auction_id]

    def get_by_bidder(self, bidder_id: str) -> List[Bid]:
        return [bid for bid in self.bids.values() if bid.bidder_id == bidder_id]

    def update(self, bid: Bid) -> Bid:
        if bid.id in self.bids:
            self.bids[bid.id] = bid
            bid.update()
        return bid


class PaymentMethod(BaseModel):
    def __init__(self, user_id: str, method_type: str, details: Dict):
        super().__init__()
        self.user_id = user_id
        self.method_type = method_type 
        self.details = details 
        self.is_default = False
        self.is_verified = False

    def set_as_default(self):
        self.is_default = True
        self.update()

    def verify(self):
        self.is_verified = True
        self.update()

class Payment(BaseModel):
    def __init__(self, auction_id: str, buyer_id: str, seller_id: str, 
                 amount: float, payment_method_id: str):
        super().__init__()
        self.auction_id = auction_id
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.amount = amount
        self.payment_method_id = payment_method_id
        self.status = PaymentStatus.PENDING
        self.transaction_id = None
        self.fee_amount = self.calculate_fee()

    def calculate_fee(self) -> float:
        return round(self.amount * 0.05, 2)

    def process(self):
        self.status = PaymentStatus.PROCESSING
        self.update()
        
        self.status = PaymentStatus.COMPLETED
        self.transaction_id = f"TXN-{uuid.uuid4()}"
        self.update()
        return True

    def refund(self):
        if self.status != PaymentStatus.COMPLETED:
            raise ValueError(f"Cannot refund payment with status: {self.status}")
            
        self.status = PaymentStatus.REFUNDED
        self.update()
        return True

class Notification(BaseModel):
    def __init__(self, user_id: str, notification_type: NotificationType, content: str, 
                 related_id: Optional[str] = None):
        super().__init__()
        self.user_id = user_id
        self.type = notification_type
        self.content = content
        self.related_id = related_id
        self.is_read = False

    def mark_as_read(self):
        self.is_read = True
        self.update()


class NotificationService:
    def __init__(self):
        self.notifications = {}

    def create_notification(self, user_id: str, notification_type: NotificationType, 
                          content: str, related_id: Optional[str] = None) -> Notification:
        notification = Notification(user_id, notification_type, content, related_id)
        self.notifications[notification.id] = notification
        self.send_notification(notification)
        return notification

    def send_notification(self, notification: Notification):
        print(f"Sending {notification.type.value} notification to user {notification.user_id}: {notification.content}")
        return True

    def get_user_notifications(self, user_id: str) -> List[Notification]:
        return [
            notification for notification in self.notifications.values() 
            if notification.user_id == user_id
        ]

    def mark_as_read(self, notification_id: str) -> bool:
        if notification_id in self.notifications:
            self.notifications[notification_id].mark_as_read()
            return True
        return False


class AuctionService:
    def __init__(
        self, 
        user_repository: UserRepository,
        item_repository: ItemRepository,
        auction_repository: AuctionRepository,
        bid_repository: BidRepository,
        notification_service: NotificationService
    ):
        self.user_repository = user_repository
        self.item_repository = item_repository
        self.auction_repository = auction_repository
        self.bid_repository = bid_repository
        self.notification_service = notification_service

    def create_auction(
        self, item_id: str, seller_id: str, start_price: float,
        start_time: datetime, end_time: datetime
    ) -> Auction:
        seller = self.user_repository.get(seller_id)
        if not seller:
            raise ValueError(f"Seller with ID {seller_id} not found")
            
        item = self.item_repository.get(item_id)
        if not item:
            raise ValueError(f"Item with ID {item_id} not found")
            
        if item.seller_id != seller_id:
            raise ValueError("Item does not belong to the seller")
            
        if start_time >= end_time:
            raise ValueError("End time must be after start time")
            
        auction = self.auction_repository.create(
            item_id, seller_id, start_price, start_time, end_time
        )
        
        seller.auctions_created.append(auction.id)
        self.user_repository.update(seller)
        
        return auction

    def place_bid(self, auction_id: str, bidder_id: str, amount: float) -> Bid:
        auction = self.auction_repository.get(auction_id)
        if not auction:
            raise ValueError(f"Auction with ID {auction_id} not found")
            
        bidder = self.user_repository.get(bidder_id)
        if not bidder:
            raise ValueError(f"Bidder with ID {bidder_id} not found")
            
        if auction.seller_id == bidder_id:
            raise ValueError("Seller cannot bid on their own auction")
            
        if auction.status != AuctionStatus.LIVE:
            raise ValueError(f"Cannot place bid on auction with status: {auction.status}")
            
        if amount <= auction.current_price:
            raise ValueError(f"Bid amount ({amount}) must be greater than current price ({auction.current_price})")
            
        bid = self.bid_repository.create(auction_id, bidder_id, amount)
        
        auction.place_bid(bid)
        self.auction_repository.update(auction)
        
        if auction_id not in bidder.auctions_participated:
            bidder.auctions_participated.append(auction_id)
            self.user_repository.update(bidder)
        
        self.notification_service.create_notification(
            auction.seller_id,
            NotificationType.NEW_BID,
            f"New bid of ${amount} placed on your auction for {self.item_repository.get(auction.item_id).name}",
            auction_id
        )
        
        if auction.current_winner_id and auction.current_winner_id != bidder_id:
            self.notification_service.create_notification(
                auction.current_winner_id,
                NotificationType.OUTBID,
                f"You've been outbid on {self.item_repository.get(auction.item_id).name}. Current price: ${amount}",
                auction_id
            )
        
        return bid

    def start_auction(self, auction_id: str) -> Auction:
        auction = self.auction_repository.get(auction_id)
        if not auction:
            raise ValueError(f"Auction with ID {auction_id} not found")
            
        auction.start_auction()
        self.auction_repository.update(auction)
        
        item = self.item_repository.get(auction.item_id)
        for user in self.user_repository.users.values():
            if auction_id in user.watchlist:
                self.notification_service.create_notification(
                    user.id,
                    NotificationType.AUCTION_START,
                    f"Auction for {item.name} has started. Starting price: ${auction.start_price}",
                    auction_id
                )
        
        return auction

    def end_auction(self, auction_id: str) -> Auction:
        auction = self.auction_repository.get(auction_id)
        if not auction:
            raise ValueError(f"Auction with ID {auction_id} not found")
            
        auction.end_auction()
        self.auction_repository.update(auction)
        
        item = self.item_repository.get(auction.item_id)
        if auction.current_winner_id:
            self.notification_service.create_notification(
                auction.current_winner_id,
                NotificationType.WINNING_BID,
                f"Congratulations! You won the auction for {item.name} with a bid of ${auction.current_price}",
                auction_id
            )
            
            self.notification_service.create_notification(
                auction.seller_id,
                NotificationType.AUCTION_END,
                f"Your auction for {item.name} has ended. Winning bid: ${auction.current_price}",
                auction_id
            )
        else:
            self.notification_service.create_notification(
                auction.seller_id,
                NotificationType.AUCTION_END,
                f"Your auction for {item.name} has ended with no bids.",
                auction_id
            )
        
        return auction

    def add_to_watchlist(self, user_id: str, auction_id: str) -> User:
        user = self.user_repository.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
            
        auction = self.auction_repository.get(auction_id)
        if not auction:
            raise ValueError(f"Auction with ID {auction_id} not found")
            
        if auction_id not in user.watchlist:
            user.watchlist.append(auction_id)
            self.user_repository.update(user)
            
        return user

    def remove_from_watchlist(self, user_id: str, auction_id: str) -> User:
        user = self.user_repository.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
            
        if auction_id in user.watchlist:
            user.watchlist.remove(auction_id)
            self.user_repository.update(user)
            
        return user


if __name__ == "__main__":
    user_repo = UserRepository()
    item_repo = ItemRepository()
    auction_repo = AuctionRepository()
    bid_repo = BidRepository()
    notification_service = NotificationService()
    
    auction_service = AuctionService(
        user_repo, item_repo, auction_repo, bid_repo, notification_service
    )
    
    seller = user_repo.create("seller_user", "seller@example.com", "password123")
    bidder1 = user_repo.create("bidder1", "bidder1@example.com", "password123")
    bidder2 = user_repo.create("bidder2", "bidder2@example.com", "password123")
    
    item = item_repo.create(
        "Vintage Watch", 
        "A rare vintage watch from the 1950s", 
        "category_watches", 
        seller.id
    )
    
    start_time = datetime.now()
    end_time = datetime(
        start_time.year, start_time.month, start_time.day, 
        start_time.hour + 1, start_time.minute
    )
    
    auction = auction_service.create_auction(
        item.id, seller.id, 100.0, start_time, end_time
    )
    
    auction_service.start_auction(auction.id)

    bid1 = auction_service.place_bid(auction.id, bidder1.id, 110.0)
    bid2 = auction_service.place_bid(auction.id, bidder2.id, 120.0)
    bid3 = auction_service.place_bid(auction.id, bidder1.id, 130.0)
    
    auction_service.add_to_watchlist(bidder2.id, auction.id)
    
    auction_service.end_auction(auction.id)
    
    print(f"Auction for {item.name} ended with winning bid: ${auction.current_price}")
    print(f"Winner: {user_repo.get(auction.current_winner_id).username}")
