from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.category_model import Category
from app.models.course_model import Course

engine = create_engine('sqlite:///cs_training.db')
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

# CATEGORY: Web Development
category1 = Category(name='Web Development')

session.add(category1)
session.commit()

course1 = Course(name='JavaScript: Understanding the Weird Parts',
                 description='In this course you will gain a deep understanding of Javascript, '
                             'learn how Javascript works under the hood, and how that knowledge '
                             'helps you avoid common pitfalls and drastically improve your ability '
                             'to debug problems. You will find clarity in the parts that others, '
                             'even experienced coders, may find weird, odd, and at times incomprehensible. '
                             'You\'ll learn the beauty and deceptive power of this language that is at the '
                             'forefront of modern software development today.',
                 img_url='https://udemy-images.udemy.com/course/750x422/364426_2991_5.jpg',
                 intro_video_url='',
                 category_id=category1.id)

session.add(course1)
session.commit()

course2 = Course(name='The Web Developer Bootcamp',
                 description='The only course you need to learn web development - HTML, CSS, JS, Node, and More!',
                 img_url='https://udemy-images.udemy.com/course/750x422/625204_436a_2.jpg',
                 intro_video_url='https://www.youtube.com/embed/P6uvOFn42NU',
                 category_id=category1.id)

session.add(course2)
session.commit()

course3 = Course(name='Build Responsive Real World Websites with HTML5 and CSS3',
                 description='Together we hand-code a beautiful and responsive landing page for '
                             'a fictional company that I made up just for the course. Step-by-step, '
                             'you will learn more and more HTML5 and CSS3 features, from beginner to advanced. '
                             'These are the latest web technologies, used by every website in the world. '
                             'And we even added some jQuery to the mix. This huge project will teach you '
                             'all the real-world skills to build real-world HTML5 and CSS3 websites. '
                             'This will allow you to build any website you can imagine... From complete scratch.',
                 img_url='https://udemy-images.udemy.com/course/750x422/437398_46c3_8.jpg',
                 intro_video_url='https://www.youtube.com/embed/H6eoOJhhqLI',
                 category_id=category1.id)

session.add(course3)
session.commit()

# CATEGORY: Mobile Apps
category2 = Category(name='Mobile Apps')

session.add(category2)
session.commit()

course1 = Course(name='The Complete Android N Developer Course',
                 description='Learn to make and market apps for Android 7 Nougat by building real apps '
                             'including Uber, Whatsapp and Instagram clones.',
                 img_url='https://udemy-images.udemy.com/course/750x422/951618_0839_2.jpg',
                 intro_video_url='https://www.youtube.com/embed/AWnbgE6YPWE',
                 category_id=category2.id)

session.add(course1)
session.commit()

course2 = Course(name='The Complete iOS 10 Developer Course',
                 description='Use Xcode 8 & Swift 3 to make real apps like Uber, Instagram & Flappy Bird. '
                             'Includes free web hosting, assets & ebook.',
                 img_url='https://udemy-images.udemy.com/course/750x422/895786_7b4b_2.jpg',
                 intro_video_url='https://www.youtube.com/embed/tEFIiPpGiCQ',
                 category_id=category2.id)

session.add(course2)
session.commit()

course3 = Course(name='Ultimate Ionic 3 - Build iOS and Android Apps with Angular 4',
                 description='Fast track your iOS and Android mobile app development '
                             'with the Ionic 3 Framework plus the power Angular 4, HTML and CSS',
                 img_url='https://udemy-images.udemy.com/course/750x422/1016960_4e24.jpg',
                 intro_video_url='',
                 category_id=category2.id)

session.add(course3)
session.commit()

course4 = Course(name='Android Material Design',
                 description='Material design is a comprehensive guide for visual, motion, '
                             'and interaction design across platforms and devices. '
                             'This course talks about all the important material design specifications, '
                             'colors, design guidelines, and also using material widgets along with material themes.',
                 img_url='https://udemy-images.udemy.com/course/480x270/921168_7646_2.jpg',
                 intro_video_url='',
                 category_id=category2.id)

session.add(course4)
session.commit()

# CATEGORY: Development Tools
category3 = Category(name='Development Tools')

session.add(category3)
session.commit()

course1 = Course(name='Docker Mastery: The Complete Toolset From a Docker Captain',
                 description='Be ready for the Dockerized future, where nearly all software is developed '
                             'and deployed in containers. Welcome to the most complete and up-to-date course '
                             'for learning and using Docker end-to-end, from development and testing, '
                             'to deployment and production. Taught by a Docker Captain and consultant.',
                 img_url='https://udemy-images.udemy.com/course/750x422/1035000_c1aa.jpg',
                 intro_video_url='',
                 category_id=category3.id)

session.add(course1)
session.commit()

course2 = Course(name='Git Complete: The definitive, step-by-step guide to Git',
                 description='This course is designed to be a comprehensive approach to Git, '
                             'which means no prior knowledge or experience is required but students will emerge '
                             'at the end with a very solid understanding and hands-on experience with Git and '
                             'related source control concepts.',
                 img_url='https://udemy-images.udemy.com/course/750x422/221674_1411_4.jpg',
                 intro_video_url='',
                 category_id=category3.id)

session.add(course2)
session.commit()


# CATEGORY: Data & Analytics
category4 = Category(name='Data & Analytics')

session.add(category4)
session.commit()

course1 = Course(name='Data Science and Machine Learning with Python - Hands On!',
                 description='Become a data scientist in the tech industry! Comprehensive data mining '
                             'and machine learning course with Python & Spark.',
                 img_url='https://udemy-images.udemy.com/course/750x422/671576_a272_3.jpg',
                 intro_video_url='',
                 category_id=category4.id)

session.add(course1)
session.commit()

course2 = Course(name='Python for Data Science and Machine Learning Bootcamp',
                 description='Learn how to use NumPy, Pandas, Seaborn, Matplotlib, Plotly, '
                             'Scikit-Learn, Machine Learning, Tensorflow, and more! This comprehensive course '
                             'will be your guide to learning how to use the power of Python to analyze data, '
                             'create beautiful visualizations, and use powerful machine learning algorithms. '
                             'This course is designed for both beginners with some programming experience or '
                             'experienced developers looking to make the jump to Data Science.',
                 img_url='https://udemy-images.udemy.com/course/750x422/903744_8eb2.jpg',
                 intro_video_url='',
                 category_id=category4.id)

session.add(course2)
session.commit()

course3 = Course(name='Deep Learning A-Z: Hands-On Artificial Neural Networks',
                 description='Learn to create Deep Learning Algorithms in Python from two Machine Learning '
                             '& Data Science experts. Templates included.',
                 img_url='https://udemy-images.udemy.com/course/750x422/1151632_de9b.jpg',
                 intro_video_url='',
                 category_id=category4.id)

session.add(course3)
session.commit()

print "added categories and courses!"
