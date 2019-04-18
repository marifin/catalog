from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Catalog, Base, SportItem, User

engine = create_engine('sqlite:///itemcatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Captain Marvel", email="iza@thisisatest.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Sport items for Soccer
catalog1 = Catalog(user_id=1, name="Soccer")

session.add(catalog1)
session.commit()

sportItem2 = SportItem(user_id=1, name="Ball", description="This brand of soccer ball was used in the last world cup.",
                     price="$15.50", catalog=catalog1)

session.add(sportItem2)
session.commit()


sportItem1 = SportItem(user_id=1, name="Goal net", description="FIFA standard size goal with net and posts",
                     price="$49.99", catalog=catalog1)

session.add(sportItem1)
session.commit()

sportItem2 = SportItem(user_id=1, name="Rebounder", description="Soccer ball will bounce right back to you.",
                     price="$69.50", catalog=catalog1)

session.add(sportItem2)
session.commit()


# Sport items for Tennis
catalog2 = Catalog(user_id=1, name="Tennis")

session.add(catalog2)
session.commit()


sportItem1 = SportItem(user_id=1, name="Racquet", description="Perfect racquet for intermediate level players.",
                     price="$120.99", catalog=catalog2)

session.add(sportItem1)
session.commit()

sportItem2 = SportItem(user_id=1, name="Balls",
                     description="Green colored felt balls for hard courts. Three per can.",
                     price="$4.99", catalog=catalog2)

session.add(sportItem2)
session.commit()

sportItem3 = SportItem(user_id=1, name="Net", description="Wimbledon standard tennis net for hard courts.",
                     price="$199.00", catalog=catalog2)

session.add(sportItem3)
session.commit()

sportItem4 = SportItem(user_id=1, name="Shoes ", description="These shoes provide perfect lateral support.",
                     price="122.00", catalog=catalog2)

session.add(sportItem4)
session.commit()

sportItem5 = SportItem(user_id=1, name="Eye Guard", description="Clear, comfortable glasses for protection on the court.",
                     price="12.99", catalog=catalog2)

session.add(sportItem5)
session.commit()

sportItem6 = SportItem(user_id=1, name="Bag", description="This bag will hold upto 4 racquets and still have room for other items.",
                     price="44.99", catalog=catalog2)

session.add(sportItem6)
session.commit()


# Sport items for snow boarding
catalog1 = Catalog(user_id=1, name="Snow Boarding")

session.add(catalog1)
session.commit()


sportItem1 = SportItem(user_id=1, name="Board", description="A cool snow board for hitting the slopes.",
                     price="$230.99", catalog=catalog1)

session.add(sportItem1)
session.commit()

sportItem2 = SportItem(user_id=1, name="Goggles", description="This goggle provides sun and wind protection for the eyes.",
                     price="$45.99", catalog=catalog1)

session.add(sportItem2)
session.commit()

sportItem3 = SportItem(user_id=1, name="Helmet", description="Best protection for the head in case of spills.",
                     price="$55.95", catalog=catalog1)

session.add(sportItem3)
session.commit()


# Sport items for Basketball
catalog1 = Catalog(user_id=1, name="Basketball")

session.add(catalog1)
session.commit()


sportItem1 = SportItem(user_id=1, name="Basketball", description="Standard size basketball.",
                     price="$10.99", catalog=catalog1)

session.add(sportItem1)
session.commit()

sportItem2 = SportItem(user_id=1, name="Hoop", description="Basketball hoop with net.",
                     price="$22.99", catalog=catalog1)

session.add(sportItem2)
session.commit()


# Sport items for Baseball
catalog1 = Catalog(user_id=1, name="Baseball")

session.add(catalog1)
session.commit()


sportItem1 = SportItem(user_id=1, name="Bat", description="Baseball bat made of wood.",
                     price="$78.95", catalog=catalog1)

session.add(sportItem1)
session.commit()

sportItem2 = SportItem(user_id=1, name="Ball", description="Baseball ball perfect for pitching.",
                     price="$4.95", catalog=catalog1)

session.add(sportItem2)
session.commit()

sportItem3 = SportItem(user_id=1, name="Gloves", description="Baseball gloves to catch that ball.",
                     price="$22.95", catalog=catalog1)

session.add(sportItem3)
session.commit()


# Sport items for Hockey
catalog1 = Catalog(user_id=1, name="Hockey")

session.add(catalog1)
session.commit()


sportItem1 = SportItem(user_id=1, name="Stick", description="Best stick on the ice rink.",
                     price="$30.95", catalog=catalog1)

session.add(sportItem1)
session.commit()

sportItem2 = SportItem(user_id=1, name="Puck", description="Great puck for ice hockey.",
                     price="$7.95", catalog=catalog1)

session.add(sportItem2)
session.commit()


# Sport items for Skating
catalog1 = Catalog(user_id=1, name="Skating")

session.add(catalog1)
session.commit()

sportItem9 = SportItem(user_id=1, name="Skates",
                     description="Skates for the ice.", price="$24.99", catalog=catalog1)

session.add(sportItem9)
session.commit()


sportItem1 = SportItem(user_id=1, name="Elbow Guards", description="Protection for elbow.",
                     price="$4.99", catalog=catalog1)

session.add(sportItem1)
session.commit()


# Sport items for Frisbee
catalog1 = Catalog(user_id=1, name="Frisbee")

session.add(catalog1)
session.commit()


sportItem1 = SportItem(user_id=1, name="Frisbee",
                     description="Plastic frisbee", price="$5.95", catalog=catalog1)

session.add(sportItem1)
session.commit()

sportItem2 = SportItem(user_id=1, name="T Shirt", description="White tshirt. ",
                     price="$7.99", catalog=catalog1)

session.add(sportItem2)
session.commit()


print "added sport items!"
