from myapp.models import User, Friend, FriendStatusEnum, Todo


def get_user_from_id(user_id):
    return User.query.filter_by(id=user_id).one()


def get_friend_status(current_user_id, other_user_id):
    """Function returning friend status between two users

    Arguments:
        current_user_id: id of user1
        other_user_id: id of user2
    
    Returns:
        tuple: In the format `(status, friend_record)` whereas `status` can be either string of
        'friend', 'pending-sent-request', 'pending-to-approve', while friend_record is an object
        of `myapp.models.Friend`
    """
    # Get and Check if has pending friend request or already a friend
    friend_record = Friend.query.filter(
                        ((Friend.user1_id == current_user_id) & (Friend.user2_id == other_user_id))\
                        | ((Friend.user2_id == current_user_id) & (Friend.user1_id == other_user_id))
                    ).one_or_none()
    # If found friend record
    if friend_record:
        if friend_record.status == FriendStatusEnum.FRIEND:
            status = 'friend'
        elif friend_record.status == FriendStatusEnum.PENDING:
            if friend_record.user1.id == int(current_user_id): # Current user sent the request
                status = 'pending-sent-request'
            else: # The other user sent the request, current user needs to approve
                status = 'pending-to-approve'
        else:
            raise Exception(f"Unknown status {friend_record.status}")
    else:
        # No record, not friend/pending, neutral
        status = 'neutral'
    return status, friend_record


def get_all_friends(current_user_id):
    """Function returning all friends of the specified user

    Arguments:
        current_user_id: id of the user that we want to get friends list
    
    Returns:
        list: A list of tuples with the format `(status, other_user)`
        whereas `status` can be either string of 'friend', 'pending-sent-request',
        'pending-to-approve', and `other_user` is a `models.User` object.

    """
    result = Friend.query.filter(
                (Friend.user1_id == current_user_id)\
                | (Friend.user2_id == current_user_id)
            ).all()
    friends = []
    for x in result:
        oth_user = x.user2 if x.user1.id == int(current_user_id) else x.user1
        if x.status == FriendStatusEnum.FRIEND:
            status = 'friend'
        elif x.status == FriendStatusEnum.PENDING:
            if x.user1.id == int(current_user_id):
                status = 'pending-sent-request'
            else:
                status = 'pending-to-approve'
        else:
            raise Exception(f"Unknown status {x.status}")
        friends.append((status, oth_user))
    return friends
