from typing import List, Dict
from datetime import datetime
from enum import Enum, auto
import uuid

class UserPrivacySettings(Enum):
    PUBLIC = auto()
    PRIVATE = auto()
    FOLLOWERS_ONLY = auto()

class NotificationType(Enum):
    LIKE = auto()
    RETWEET = auto()
    FOLLOW = auto()
    MENTION = auto()
    COMMENT = auto()

class User:
    def __init__(self, username: str, email: str, password: str):
        self.user_id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = self._hash_password(password)
        self.profile_picture = None
        self.bio = ""
        self.followers: List[str] = []  # List of user_ids
        self.following: List[str] = []  # List of user_ids
        self.privacy_setting = UserPrivacySettings.PUBLIC
        self.created_at = datetime.now()

    def _hash_password(self, password: str) -> str:
        # Implement secure password hashing (e.g., bcrypt)
        return hash(password)

    def update_profile(self, bio: str = None, profile_picture: str = None):
        if bio:
            self.bio = bio
        if profile_picture:
            self.profile_picture = profile_picture

    def set_privacy(self, privacy: UserPrivacySettings):
        self.privacy_setting = privacy

class Tweet:
    def __init__(self, user_id: str, content: str, media: List[str] = None):
        self.tweet_id = str(uuid.uuid4())
        self.user_id = user_id
        self.content = content
        self.media = media or []
        self.created_at = datetime.now()
        self.likes: List[str] = []  # List of user_ids who liked
        self.retweets: List[str] = []  # List of user_ids who retweeted
        self.comments: List['Comment'] = []
        self.hashtags: List[str] = self._extract_hashtags()

    def _extract_hashtags(self) -> List[str]:
        return [word for word in self.content.split() if word.startswith('#')]

class Comment:
    def __init__(self, user_id: str, tweet_id: str, content: str):
        self.comment_id = str(uuid.uuid4())
        self.user_id = user_id
        self.tweet_id = tweet_id
        self.content = content
        self.created_at = datetime.now()
        self.likes: List[str] = []

class Notification:
    def __init__(self, user_id: str, source_user_id: str, 
                 notification_type: NotificationType, 
                 reference_id: str):
        self.notification_id = str(uuid.uuid4())
        self.user_id = user_id
        self.source_user_id = source_user_id
        self.type = notification_type
        self.reference_id = reference_id  # tweet_id or comment_id
        self.created_at = datetime.now()
        self.is_read = False

class TwitterService:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.tweets: Dict[str, Tweet] = {}
        self.notifications: Dict[str, List[Notification]] = {}

    def register_user(self, username: str, email: str, password: str) -> User:
        # Check for existing username/email
        user = User(username, email, password)
        self.users[user.user_id] = user
        return user

    def create_tweet(self, user_id: str, content: str, media: List[str] = None) -> Tweet:
        # Validate user exists
        if user_id not in self.users:
            raise ValueError("User not found")
        
        tweet = Tweet(user_id, content, media)
        self.tweets[tweet.tweet_id] = tweet
        return tweet

    def follow_user(self, follower_id: str, followee_id: str):
        # Validate users exist
        if follower_id not in self.users or followee_id not in self.users:
            raise ValueError("User not found")
        
        # Add to followers/following lists
        self.users[follower_id].following.append(followee_id)
        self.users[followee_id].followers.append(follower_id)
        
        # Create notification
        self._create_notification(
            followee_id, 
            follower_id, 
            NotificationType.FOLLOW, 
            follower_id
        )

    def like_tweet(self, user_id: str, tweet_id: str):
        # Validate user and tweet exist
        if user_id not in self.users or tweet_id not in self.tweets:
            raise ValueError("User or Tweet not found")
        
        tweet = self.tweets[tweet_id]
        if user_id not in tweet.likes:
            tweet.likes.append(user_id)
            
            # Create notification for tweet owner
            self._create_notification(
                tweet.user_id, 
                user_id, 
                NotificationType.LIKE, 
                tweet_id
            )

    def _create_notification(self, 
                              user_id: str, 
                              source_user_id: str, 
                              notification_type: NotificationType, 
                              reference_id: str):
        notification = Notification(
            user_id, 
            source_user_id, 
            notification_type, 
            reference_id
        )
        
        if user_id not in self.notifications:
            self.notifications[user_id] = []
        
        self.notifications[user_id].append(notification)

    def get_user_timeline(self, user_id: str, limit: int = 50) -> List[Tweet]:
        user = self.users.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        timeline_tweets = []
        for tweet_id, tweet in self.tweets.items():
            if (tweet.user_id == user_id or 
                tweet.user_id in user.following):
                timeline_tweets.append(tweet)
        
        return sorted(
            timeline_tweets, 
            key=lambda t: t.created_at, 
            reverse=True
        )[:limit]

if __name__ == 'main':
    twitter = TwitterService()
    
    user1 = twitter.register_user("alice", "alice@example.com", "password123")
    user2 = twitter.register_user("bob", "bob@example.com", "password456")
    
    twitter.follow_user(user1.user_id, user2.user_id)
    tweet = twitter.create_tweet(user2.user_id, "Hello, Twitter! #welcome")
    twitter.like_tweet(user1.user_id, tweet.tweet_id)
    
    timeline = twitter.get_user_timeline(user1.user_id)
    print(f"Timeline for {user1.username}: {len(timeline)} tweets")