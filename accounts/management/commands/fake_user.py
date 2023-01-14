from django.core.management.base import BaseCommand
from faker import Faker
from accounts.models import User
import random


faker = Faker()
count = 120

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

last_names_list = []
while len(last_names_list) < count:
    last_name = faker.last_name()
    if last_name not in last_names_list:
        last_names_list.append(last_name)

names_list = [faker.name() for _ in range(count)]

email_list = [faker.email() for _ in range(count)]



class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        for i in range(count):
            print(f'{i}/{count}')

            user = User.objects.create(
                name = names_list[i],
                family = last_names_list[i],
                username = names_list[i],
                skills = skills_list[i],
                email = email_list[i],
                about = faker.paragraph(nb_sentences=random.randint(1, 10))
            )
            username = user.username
            username = username.replace('.', '')
            username = username.replace(' ', '_')
            username = username.lower()
            user.username = username
            user.save()


