from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum, auto

class ConnectionStatus(Enum):
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    BLOCKED = 'BLOCKED'

class PrivacySetting(Enum):
    PUBLIC = 'PUBLIC'
    CONNECTIONS_ONLY = 'CONNECTIONS_ONLY'
    PRIVATE = 'PRIVATE'

class NotificationType(Enum):
    CONNECTION_REQUEST = 'CONNECTION_REQUEST'
    CONNECTION_ACCEPTED = 'CONNECTION_ACCEPTED'
    POST_LIKE = 'POST_LIKE'
    COMMENT = 'COMMENT'

class User:
    def __init__(self, user_id: str, name: str, email: str, headline: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.headline = headline
        self.connections: List[Connection] = []
        self.profile = Profile(user_id)
        self.feed = Feed(user_id)
        self.notifications = NotificationManager(user_id)
        self.privacy_settings: Dict[str, PrivacySetting] = {}
    
    def send_connection_request(self, target_user: 'User') -> Connection:
        """Send a connection request to another user"""
        connection = Connection(self, target_user)
        target_user.receive_connection_request(connection)
        return connection

    def receive_connection_request(self, connection: 'Connection'):
        """Receive and handle a connection request"""
        self.notifications.add_notification(
            Notification(
                f"New connection request from {connection.sender.name}",
                NotificationType.CONNECTION_REQUEST
            )
        )
    
    def accept_connection_request(self, connection: 'Connection'):
        """Accept a connection request"""
        connection.status = ConnectionStatus.ACCEPTED
        self.connections.append(connection)
        self.notifications.add_notification(
            Notification(
                f"Connection request from {connection.sender.name} accepted",
                NotificationType.CONNECTION_ACCEPTED
            )
        )

class Profile:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.experience: List[Experience] = []
        self.education: List[Education] = []
        self.skills: List[Skill] = []
        self.achievements: List[Achievement] = []

    def add_experience(self, experience: 'Experience'):
        """Add work experience to profile"""
        self.experience.append(experience)

    def add_education(self, education: 'Education'):
        """Add education details to profile"""
        self.education.append(education)
    
class Experience:
    def __init__(self, company: str, title: str, start_date: datetime, 
                 end_date: Optional[datetime] = None, 
                 description: Optional[str] = None):
        self.company = company
        self.title = title
        self.start_date = start_date
        self.end_date = end_date
        self.description = description

class Education:
    def __init__(self, institution: str, degree: str, 
                 start_year: int, end_year: int, 
                 additional_info: Optional[str] = None):
        self.institution = institution
        self.degree = degree
        self.start_year = start_year
        self.end_year = end_year
        self.additional_info = additional_info

class Skill:
    def __init__(self, name: str, endorsement_count: int = 0):
        self.name = name
        self.endorsement_count = endorsement_count

class Achievement:
    def __init__(self, title: str, description: Optional[str] = None):
        self.title = title
        self.description = description

class Connection:
    def __init__(self, sender: User, receiver: User):
        self.sender = sender
        self.receiver = receiver
        self.status = ConnectionStatus.PENDING
        self.connection_date: Optional[datetime] = None

    def update_status(self, new_status: ConnectionStatus):
        """Update connection status"""
        self.status = new_status
        if new_status == ConnectionStatus.ACCEPTED:
            self.connection_date = datetime.now()

class Post:
    def __init__(self, user: User, content: str):
        self.post_id = self._generate_post_id()
        self.user = user
        self.content = content
        self.timestamp = datetime.now()
        self.likes: List[User] = []
        self.comments: List[Comment] = []

    def _generate_post_id(self) -> str:
        """Generate a unique post ID"""
        return f"POST_{datetime.now().timestamp()}"

    def add_like(self, user: User):
        """Add a like to the post"""
        if user not in self.likes:
            self.likes.append(user)

    def add_comment(self, comment: 'Comment'):
        """Add a comment to the post"""
        self.comments.append(comment)

class Comment:
    def __init__(self, user: User, content: str):
        self.user = user
        self.content = content
        self.timestamp = datetime.now()

class Feed:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.posts: List[Post] = []

    def create_post(self, user: User, content: str) -> Post:
        """Create a new post in the feed"""
        post = Post(user, content)
        self.posts.append(post)
        return post
    
class Notification:
    def __init__(self, message: str, notification_type: NotificationType):
        self.message = message
        self.type = notification_type
        self.timestamp = datetime.now()
        self.is_read = False

class NotificationManager:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.notifications: List[Notification] = []

    def add_notification(self, notification: Notification):
        """Add a new notification"""
        self.notifications.append(notification)

    def mark_as_read(self, notification: Notification):
        """Mark a specific notification as read"""
        notification.is_read = True

if __name__ == "__main__":
    john = User("user_001", "John Doe", "john@example.com", "Software Engineer")
    jane = User("user_002", "Jane Smith", "jane@example.com", "Product Manager")

    john.profile.add_experience(
        Experience(
            "Tech Corp", 
            "Senior Software Engineer", 
            datetime(2020, 1, 1), 
            description="Leading backend development"
        )
    )

    connection = john.send_connection_request(jane)
    jane.accept_connection_request(connection)

    post = john.feed.create_post(john, "Excited about my new project!")
    post.add_like(jane)
    post.add_comment(Comment(jane, "Sounds interesting!"))
