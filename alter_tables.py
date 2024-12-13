import ast
from cmath import log
import re
import smtplib
import json
import math
# from tkinter.messagebox import NO
from datetime import date, datetime, timedelta
import pandas as pd
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.db.models import OuterRef, Subquery
from django.core.mail import send_mail 
from django.template.loader import render_to_string
from django.db.models import Q, Sum,Avg, F, Count, Value
from fiscalyear import *
import fiscalyear
import numpy
from django.db import connection
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
import datetime
from datetime import datetime, timedelta
from django.contrib.auth.models import User, Group, GroupManager
import uuid
from django.db.models import Q
################### API's ################################
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status

from SupplyChainManagement_AHLL import settings
################### END API's ###########################
################### Forms Import #####################
from .forms import shift_insert
################### End Forms Import #################

######################## Views Import ############################
from .approvaldesk import approvaldeskglobal
####################### End Views Import #########################

################### Models Import #####################
from .models import *
from .emp_models import *
from .login_models import *
################### End Models Import #################
config_data = settings.CONFIG_DATA

from django.apps import apps
from django.db import connection
from collections import defaultdict

def alter_tables(request):
    all_models = apps.get_models()
    print('alter_tablesalter_tablesalter_tablesalter_tablesalter_tablesalter_tablesalter_tablesalter_tables')

    # Mapping of Django field types to MySQL data types
    django_to_mysql_types = {
        models.AutoField: 'INT',
        models.BigIntegerField: 'BIGINT',
        models.BooleanField: 'BOOL',
        models.CharField: 'VARCHAR',
        models.CommaSeparatedIntegerField: 'VARCHAR',
        models.DateField: 'DATE',
        models.DateTimeField: 'DATETIME',
        models.DecimalField: 'DECIMAL',
        models.EmailField: 'VARCHAR',
        models.FileField: 'VARCHAR',
        models.FilePathField: 'VARCHAR',
        models.ForeignKey: 'INT',
        models.FloatField: 'FLOAT',
        models.ImageField: 'VARCHAR',
        models.IntegerField: 'INT',
        models.GenericIPAddressField: 'VARCHAR',
        models.NullBooleanField: 'BOOL',
        models.PositiveIntegerField: 'INT',
        models.PositiveSmallIntegerField: 'SMALLINT',
        models.SlugField: 'VARCHAR',
        models.SmallIntegerField: 'SMALLINT',
        models.TextField: 'TEXT',
        models.TimeField: 'TIME',
        models.URLField: 'VARCHAR',
        models.UUIDField: 'VARCHAR',
    }
    alters = []
    unknown = []
    tables = []
    # Get a cursor for the database connection
    with connection.cursor() as cursor:

        # Get the column names and types for each model's database table
        for model in all_models:
            try:
                table_name = model._meta.db_table
                cursor.execute(f"DESCRIBE {table_name}")
                db_columns_info = cursor.fetchall()
                # Create a set of existing column names
                existing_columns = set(row[0] for row in db_columns_info)

                # Compare the model's field names with the database columns
                for field in model._meta.fields:
                    column_name = field.column
                    if column_name not in existing_columns:
                        field_type = type(field)
                        if field_type in django_to_mysql_types:
                            mysql_type = django_to_mysql_types[field_type]
                            max_length = field.max_length if isinstance(field, models.CharField) else None
                            if max_length:
                                column_type = f'{mysql_type}({max_length})'
                            else:
                                column_type = mysql_type
                            ddl_statement = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};"
                            alters.append(ddl_statement)
                            print(ddl_statement)
                        else:
                            d = f"Unknown column type: {column_name} in table {table_name}"
                            unknown.append(d)
                            print(d)           
            except Exception as e:
                tables.append(e)
    lists = {'Alter Commands': alters, 'Unknown Columns': unknown, 'Tables': tables}

    # Generate the HTML structure
    template = ''
    for name, content in lists.items():
        template += f'''
            <h2>{name}</h2>
            <ul>
                {''.join(f'<li>{item}</li>' for item in content)}
            </ul>
           
        '''
    print(template,'tetetetetetetetet')
    return HttpResponse(template)
