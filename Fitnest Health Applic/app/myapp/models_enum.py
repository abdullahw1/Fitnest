import enum

class FriendStatusEnum(enum.Enum):
    """Enum representing friend status in database
    
    Attributes:
        PENDING: Friend request is still pending on someone to approve/reject it
        FRIEND: Friend request was approved and two user is now friend    
    """
    PENDING = 0
    FRIEND = 1