from django.test import TestCase

import os
from urllib import parse
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_world.settings')
    import django
    django.setup()

    from blog import models
    from user.models import Attention
    from django.db.models import Count

    obj1 = models.Classify.objects.filter(id=1).first()
    obj2 = models.Classify.objects.filter(id=8).first()

    print(obj1.sort, obj2.sort)

    obj1.sort, obj2.sort = obj2.sort, obj1.sort

    print(obj1.sort, obj2.sort)
    obj1.save()
