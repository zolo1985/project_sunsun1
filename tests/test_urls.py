# import unittest
# import json
# # from webapp import create_app
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from webapp import models
# from webapp.database import Base
# from sqlalchemy.orm import scoped_session, sessionmaker


# class TestURLs(unittest.TestCase):
#     def setUp(self):

#         database_connection_uri = ("mysql+pymysql://root:swainers1@localhost/sunsundatabase1?charset=utf8mb4")
#         self.engine = create_engine(database_connection_uri, pool_size=20, max_overflow=0, pool_timeout=30, pool_recycle=1800, pool_pre_ping=True)
#         self.session = scoped_session(sessionmaker(autocommit=False,
#                                          autoflush=False,
#                                          bind=self.engine))

#         Base = declarative_base()
#         Base.query = self.session.query_property()
#         Base.metadata.create_all(bind=self.engine)

#         user = models.User()
#         user.company_name = "solo12"
#         user.firstname = "John"
#         user.lastname = "Doe"
#         user.email = "solo12@gmail.com"
#         user.password = "password"
#         self.session.add(user)
#         self.session.commit()
#         self.client = self.app.test_client()


#     def tearDown(self):
#         self.session.remove()

#     def test_root_redirect(self):
#            """ Tests if the root URL gives a 302 """
#            result = self.client.get('/')
#            assert result.status_code == 302
#            assert "/blog/" in result.headers['Location']


# if __name__ == '__main__':
#     unittest.main()