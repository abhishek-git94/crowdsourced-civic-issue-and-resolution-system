from datetime import datetime
from mongoengine import (
    Document, StringField, IntField, FloatField, DateTimeField, 
    ReferenceField, BooleanField, ListField, CASCADE
)
from flask_login import UserMixin

class User(Document, UserMixin):
    meta = {'collection': 'users'}
    
    name = StringField(max_length=100, required=True)
    email = StringField(max_length=200, unique=True, required=True)
    password = StringField(max_length=255, required=True)
    role = StringField(max_length=50, default="citizen")
    points = IntField(default=0)
    phone_number = StringField(max_length=20)
    fcm_token = StringField(max_length=255)

    def __repr__(self) -> str:
        return f"<User id={self.id} name={self.name} email={self.email}>"

    @property
    def issues(self):
        return Issue.objects(user=self.id)

    @property
    def upvotes(self):
        return Upvote.objects(user=self.id)

class Issue(Document):
    meta = {'collection': 'issues'}

    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    
    name = StringField(max_length=100, required=True)
    issue = StringField(required=True)
    location = StringField(max_length=200, required=True)
    latitude = FloatField()
    longitude = FloatField()
    file = StringField(max_length=200)

    status = StringField(max_length=50, default="Pending")
    category = StringField(max_length=100)
    confidence = FloatField()
    severity = StringField(max_length=50)
    assigned_to = StringField(max_length=100)
    
    is_confirmed_by_citizen = BooleanField(default=False)
    resolved_at = DateTimeField()

    is_duplicate_of = ReferenceField('self')
    embedding = StringField()

    upvotes = IntField(default=0)
    created_at = DateTimeField(default=datetime.utcnow)

    def __repr__(self):
        return f"<Issue id={self.id} issue={self.issue[:20]}>"

    @property
    def upvote_records(self):
        return Upvote.objects(issue=self.id)

class Upvote(Document):
    meta = {
        'collection': 'upvotes',
        'indexes': [
            {'fields': ('user', 'issue'), 'unique': True}
        ]
    }

    user = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    issue = ReferenceField(Issue, required=True, reverse_delete_rule=CASCADE)

    def __repr__(self):
        return f"<Upvote user={self.user.id} issue={self.issue.id}>"

class ForumPost(Document):
    meta = {'collection': 'forum_posts'}
    
    user = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    title = StringField(max_length=200, required=True)
    content = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)

class ForumComment(Document):
    meta = {'collection': 'forum_comments'}
    
    post = ReferenceField(ForumPost, required=True, reverse_delete_rule=CASCADE)
    user = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    content = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)

    @property
    def comments(self):
        return ForumComment.objects(post=self.id)

class Message(Document):
    meta = {'collection': 'messages'}
    
    sender = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    receiver = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    issue = ReferenceField(Issue, reverse_delete_rule=CASCADE)
    content = StringField(required=True)
    is_read = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
