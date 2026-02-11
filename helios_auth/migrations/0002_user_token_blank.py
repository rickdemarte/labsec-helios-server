# -*- coding: utf-8 -*-

from django.db import migrations
import helios_auth.jsonfield


class Migration(migrations.Migration):

    dependencies = [
        ("helios_auth", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="token",
            field=helios_auth.jsonfield.JSONField(null=True, blank=True),
        ),
    ]
