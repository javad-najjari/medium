import random, os
from faker import Faker
from ...models import User
from ...models import Post, File
from .get_time import create_time
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile


fake = Faker()

title_list = [
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

        for i in range(200):
            x = random.randint(1, 15)
            user = random.choice(users)
            tags = random.sample(title_list, random.randint(1, 5))
            new_tags = []
            for tag in tags:
                new_tags.append(tag.replace(' ', '_'))
            print(f'create post: {i+1} / 200  ->  {user}')

            Post.objects.create(
                user = user,
                title = random.choice(title_list),
                tags = ','.join(new_tags),
                description = fake.paragraph(nb_sentences=x),
                created = create_time()
            )
        

        posts = Post.objects.all()
        posts = [post for post in posts]
        images = os.listdir('/home/javad/Desktop/image/')
        rand = random.sample(list(range(0, 733)), 733)
        counter = len(posts)
        i, x = 1, 0

        for post in posts:
            count = random.randint(1, 5)
            print(f'post file: {i} / {counter}')
            if x > 727:
                rand = random.sample(list(range(0, 733)), 733)
                x = 0

            for _ in range(count):

                # rand = random.randint(0, 733)
                directory = f'/home/javad/Desktop/image/{images[rand[x]]}'

                with open(directory, 'rb') as f:
                        data = f.read()

                file = File(post=post)
                file.file.save(images[rand[x]], ContentFile(data))
                x += 1
            i += 1

