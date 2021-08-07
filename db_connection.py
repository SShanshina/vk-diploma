import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, Session

engine = sq.create_engine('postgresql://vk_diploma:vk_diploma@localhost:5432/vk_diploma')
connection = engine.connect()
Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id = sq.Column(sq.Integer, primary_key=True, unique=True)
    user_id = sq.Column(sq.Integer)


session = Session(connection)


def check_db(user_search_id):
    get_data = session.query(Users).all()
    for item in get_data:
        if user_search_id != item.user_id:
            new_user = Users(user_id=user_search_id)
            session.add(new_user)
            session.commit()
        else:
            pass
