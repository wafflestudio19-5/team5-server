from django.test import TestCase
from factory.django import DjangoModelFactory
from faker import Faker

from user.models import User
from django.test import TestCase
from django.db import transaction
from rest_framework import status
import json

from user.serializers import jwt_token_of

class UserSignupTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.correct_data = {
            'username' : 'test',
            'password' : '1234',
            'email' : 'test@test.com',
            'nickname' : 'testnick',
            'admission_year' : '20학번',
            'univ' : '서울대학교'
        }

    def make_fake_user_data(self, **kwargs):
        data = self.correct_data
        fake = Faker()
        data['username'] = fake.name()
        data['email'] = fake.email()
        data['nickname'] = fake.name()
        for key, value in kwargs.items():
            data[key] = value
        return data

    def test_signup(self):
        response = self.client.post('/user/signup/', data=self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admission_year(self):
        for year in ['23학번', '09학번', '졸업자', '17']:
            data = self.make_fake_user_data(admission_year=year)
            response = self.client.post('/user/signup/', data=data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for year in ['17학번', '10학번', '22학번', '15학번', '그 외 학번', '졸업생']:
            data = self.make_fake_user_data(admission_year=year)
            response = self.client.post('/user/signup/', data=data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

