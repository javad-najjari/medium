import random, os
from accounts.models import User, BookMark, BookMarkUser
from post.models import Post
from django.core.management.base import BaseCommand



skills_list = [
    'Active_listening', 'Storytelling', 'Written_communication', 'Editing', 'Teaching', 'Negotiating',
    'Open-mindedness', 'Inquiring', 'Body_language', 'Customer_service', 'Presenting', 'Summarizing',
    'Nonverbal_communication', 'Documenting', 'Reporting', 'Patience', 'Positivity', 'Conflict_management',
    'Coaching', 'Mediating', 'Motivating', 'Compassion', 'Caring', 'Networking', 'Inspiring', 'Flexibility',
    'Collaboration', 'Sourcing_feedback', 'Reliability', 'Empathy', 'Observing', 'Problem-solving', 'Inferring',
    'Simplifying', 'Conceptual_thinking', 'Evaluating', 'Streamlining', 'Creative_thinking', 'Brainstorming',
    'Cost-benefit_analyzing', 'Deductive_reasoning', 'Inductive_reasoning', 'Assessing', 'Evidence_collecting',
    'Troubleshooting', 'Mentoring', 'Envisioning', 'Goal-setting', 'Employee_development',
    'Performance_reviewing', 'Managing', 'Planning', 'Delegating', 'Directing', 'Supervising', 'Training',
    'Earning_trust', 'Influencing', 'Adapting', 'Crisis_managing', 'Accounting', 'Word_processing',
    'Spreadsheet_building', 'Coding', 'Programming', 'Operating_equipment', 'Engineering', 'Experimenting',
    'Testing', 'Constructing', 'Restoring', 'Product_developing', 'Quality_controlling', 'Blueprint_drafting',
    'Repairing', 'Translating', 'Speaking', 'Writing', 'Conversing', 'Reinterpreting', 'Public_speaking',
    'Following_etiquette', 'Explaining', 'Respecting', 'Signaling', 'Proofreading', 'Introducing',
    'Representing', 'Rephrasing', 'Code-switching', 'Graphic_designing', 'Illustrating', 'Sketching',
    'Architecture', 'User_experience_development', 'User_interface_development', 'Typography',
    'Layout_development', 'Web_designing', 'Interior_designing', 'Data_visualizing', 'Hierarchical_arranging',
    'Aligning', 'Photo_and_video_editing', 'Wireframing', 'Researching', 'Interpreting',
    'Information_processing', 'Organizing', 'Processing', 'Graphing', 'Computing', 'Calculating', 'Modeling',
    'Extrapolating', 'Predicting', 'Forecasting', 'Investigating', 'Surveying', 'Statistical_analysis'
    ]


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.all()
        users = [user for user in users]
        counter = len(users)
        i = 1
        
        for user in users:
            rand = random.randint(1, 5)
            titles = random.sample(skills_list, rand)
            print(f'book_mark: {i} / {counter}')
            for x in range(rand):
                BookMark.objects.create(
                    title = titles[x],
                    user = random.choice(users)
                )
            i += 1
        

        book_marks = BookMark.objects.all()
        book_marks = [book_mark for book_mark in book_marks]

        posts = Post.objects.all()
        posts = [post for post in posts]

        counter = len(book_marks)
        i = 1

        for book_mark in book_marks:
            rand = random.randint(1, 10)
            new_posts = random.sample(posts, rand)
            print(f'bookmark_user: {i} / {counter}')

            for new_post in new_posts:
                BookMarkUser.objects.create(
                    book_mark = book_mark,
                    post = new_post
                )
            i += 1

