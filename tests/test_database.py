from user_data.database import Database


def test_insert_message():
    db = Database()
    user_id = 1
    db.create_user_if_not_exist(user_id=user_id, username="default")
    db.get_last_interaction_timestamp(user_id)
    assert len(db.users)==1