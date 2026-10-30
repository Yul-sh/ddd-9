from faker import Faker
from locust import HttpUser, task, SequentialTaskSet, TaskSet, constant_throughput
import random

fake = Faker('ru_RU')
print(fake.name())

class BrowseApiTasks(TaskSet):
    @task(5)
    def get_health(self):
        self.client.get('/api/health')

    @task(5)
    def get_tours(self):
        self.client.get('/api/tours')

    @task(5)
    def get_tour_detail(self):
        tour_id = random.randint(1, 12)
        self.client.get('/api/tours/{}'.format(tour_id), name='/api/tours/[id]')

    @task(5)
    def get_reviews(self):
        tour_id = random.randint(1, 12)
        self.client.get(
            '/api/reviews?tour_id={}'.format(tour_id),
            name='/api/reviews?tour_id=[id]'
        )

    @task(1)
    def add_tourist(self):
        tourist_data = {
            'email': fake.unique.email(),
            'password': fake.password(length=10),
            'full_name': '{} {} {}'.format(
                fake.last_name_female(),
                fake.first_name_female(),
                fake.middle_name_female()
            ),
            'phone': str(fake.random_int(min=9000000000, max=9999999999)),
        }
        self.client.post('/api/auth/register', json=tourist_data)

class TouristJourney(SequentialTaskSet):
    @task
    def get_tours(self):
        self.client.get('/api/tours')

    @task
    def add_tourist(self):
        tourist_data = {
            'email': fake.unique.email(),
            'password': fake.password(length=10),
            'full_name': '{} {} {}'.format(
                fake.last_name_female(),
                fake.first_name_female(),
                fake.middle_name_female()
            ),
            'phone': str(fake.random_int(min=9000000000, max=9999999999)),
        }
        self.client.post('/api/auth/register', json=tourist_data)
        self.interrupt()

class WebsiteUser(HttpUser):
    wait_time = constant_throughput(2)
    tasks = {BrowseApiTasks: 3, TouristJourney: 1}
