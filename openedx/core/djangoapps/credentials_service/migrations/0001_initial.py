# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import openedx.core.djangoapps.credentials_service.models
import model_utils.fields
import xmodule_django.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificateTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('content', models.TextField(help_text='HTML Template content data.')),
                ('certificate_type', models.CharField(blank=True, max_length=255, null=True, choices=[('Honor', 'honor'), ('Verified', 'verified'), ('Professional', 'professional')])),
                ('organization_id', models.IntegerField(help_text='Organization with which this template is attached.', null=True, db_index=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CertificateTemplateAsset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('name', models.CharField(max_length=255)),
                ('asset_file', models.FileField(upload_to=openedx.core.djangoapps.credentials_service.models.template_assets_path)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CourseCertificate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('is_active', models.BooleanField(default=False)),
                ('title', models.CharField(help_text='Custom certificate title to override default display_name for a course/program.', max_length=255, null=True, blank=True)),
                ('course_id', xmodule_django.models.CourseKeyField(max_length=255)),
                ('certificate_type', models.CharField(max_length=255, choices=[('Honor', 'honor'), ('Verified', 'verified'), ('Professional', 'professional')])),
            ],
        ),
        migrations.CreateModel(
            name='ProgramCertificate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('is_active', models.BooleanField(default=False)),
                ('title', models.CharField(help_text='Custom certificate title to override default display_name for a course/program.', max_length=255, null=True, blank=True)),
                ('program_id', models.PositiveIntegerField(db_index=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Signatory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('name', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('image', models.ImageField(help_text='Image must be square PNG files. The file size should be under 250KB.', upload_to=openedx.core.djangoapps.credentials_service.models.signatory_assets_path, validators=[openedx.core.djangoapps.credentials_service.models.validate_image])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserCredential',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('credential_id', models.PositiveIntegerField()),
                ('username', models.CharField(max_length=255, db_index=True)),
                ('status', models.CharField(default='awarded', max_length=255, choices=[('awarded', 'awarded'), ('revoked', 'revoked')])),
                ('download_url', models.CharField(help_text='Download URL for the PDFs.', max_length=255, null=True, blank=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('credential_content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='UserCredentialAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('namespace', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=255)),
                ('user_credential', models.ForeignKey(to='credentials_service.UserCredential')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='programcertificate',
            name='signatories',
            field=models.ManyToManyField(to='credentials_service.Signatory'),
        ),
        migrations.AddField(
            model_name='programcertificate',
            name='site',
            field=models.ForeignKey(to='sites.Site'),
        ),
        migrations.AddField(
            model_name='programcertificate',
            name='template',
            field=models.ManyToManyField(to='credentials_service.CertificateTemplate', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='coursecertificate',
            name='signatories',
            field=models.ManyToManyField(to='credentials_service.Signatory'),
        ),
        migrations.AddField(
            model_name='coursecertificate',
            name='site',
            field=models.ForeignKey(to='sites.Site'),
        ),
        migrations.AddField(
            model_name='coursecertificate',
            name='template',
            field=models.ManyToManyField(to='credentials_service.CertificateTemplate', null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='usercredential',
            unique_together=set([('username', 'credential_content_type', 'credential_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='coursecertificate',
            unique_together=set([('course_id', 'certificate_type', 'site')]),
        ),
    ]
