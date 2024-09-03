import json
import requests
import stripe
import random
import string
import time
import os
import logging
import datetime
import pandas as pd
from django.utils import timezone
from django.conf import settings
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.crypto import get_random_string
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from .models import *
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup  
from django.utils.dateparse import parse_datetime
from celery import shared_task
from celery import chain
from celery import Celery, chain
from celery.schedules import crontab
from django.core.mail import send_mail
from selenium.webdriver.chrome.options import Options
from lxml import html
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

