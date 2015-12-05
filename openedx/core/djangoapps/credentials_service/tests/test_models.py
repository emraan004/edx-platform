"""Test models for credentials service app."""
from path import Path

from django.test import TestCase
from django.contrib.sites.models import Site
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from opaque_keys.edx.locator import CourseLocator

from openedx.core.djangoapps.credentials_service.models import (
    CertificateTemplate, CertificateTemplateAsset,
    CourseCertificate, ProgramCertificate,
    Signatory, UserCredential, UserCredentialAttribute
)

# pylint: disable=invalid-name
TEST_DIR = Path(__file__).dirname()
TEST_DATA_DIR = 'common/test/data/'
PLATFORM_ROOT = TEST_DIR.parent.parent.parent.parent.parent
TEST_DATA_ROOT = PLATFORM_ROOT / TEST_DATA_DIR


class TestSignatory(TestCase):
    """Test Signatory model."""
    def get_image(self, name):
        """Get one of the test images from the test data directory."""
        return ImageFile(open(TEST_DATA_ROOT / 'credentials' / name + '.png'))

    def create_clean(self, file_obj):
        """
        Shortcut to create a Signatory with a specific file.
        """
        Signatory(name="test_signatory", title="Test Signatory", image=file_obj).full_clean()

    def test_good_image(self):
        """Verify that saving a valid signatory image is no problem."""
        good_image = self.get_image("good")
        Signatory(name="test_signatory", title="Test Signatory", image=good_image).full_clean()

    def test_large_image(self):
        """Upload of large image size should raise validation exception."""
        large_image = self.get_image("large")
        self.assertRaises(ValidationError, self.create_clean, large_image)

    def test_signatory_file_saving(self):
        """
        Verify that signatory image file is saving with actual name and on correct path.
        """
        Signatory.objects.create(name='test name', title='test title', image=SimpleUploadedFile(
            'picture1.jpg',
            'image contents!')).save()
        signatory = Signatory.objects.get(id=1)
        self.assertEqual(signatory.image, 'signatories/1/picture1.jpg')

    def test_unicode_value(self):
        """Test unicode value is correct."""
        Signatory.objects.create(name='test name', title='test title', image=SimpleUploadedFile(
            'picture1.jpg',
            'image contents!')).save()
        signatory = Signatory.objects.get(id=1)
        self.assertEqual(unicode(signatory), "test name, test title")


class TestCertificateTemplate(TestCase):
    """Test CertificateTemplate model."""

    def test_unicode_value(self):
        """Test unicode value is correct."""
        certificate_template = CertificateTemplate.objects.create(name="test name", content="test content")
        self.assertEqual(unicode(certificate_template), "test name")


class TestCertificateTemplateAsset(TestCase):
    """
    Test Assets are uploading/saving successfully for CertificateTemplateAsset.
    """
    def test_asset_file_saving(self):
        """
        Verify that asset file is saving with actual name and on correct path.
        """
        CertificateTemplateAsset.objects.create(name='test name', asset_file=SimpleUploadedFile(
            'picture1.jpg',
            'file contents!')).save()
        certificate_template_asset = CertificateTemplateAsset.objects.get(id=1)
        self.assertEqual(
            certificate_template_asset.asset_file, 'credential_certificate_template_assets/1/picture1.jpg'
        )

        # Now save asset with same file again, New file will be uploaded after deleting the old one with the same name.
        certificate_template_asset.asset_file = SimpleUploadedFile('picture1.jpg', 'file contents')
        certificate_template_asset.save()
        self.assertEqual(
            certificate_template_asset.asset_file, 'credential_certificate_template_assets/1/picture1.jpg'
        )

        # Now replace the asset with another file
        certificate_template_asset.asset_file = SimpleUploadedFile('picture2.jpg', 'file contents')
        certificate_template_asset.save()

        certificate_template_asset = CertificateTemplateAsset.objects.get(id=1)
        self.assertEqual(
            certificate_template_asset.asset_file, 'credential_certificate_template_assets/1/picture2.jpg'
        )

    def test_unicode_value(self):
        """Test unicode value is correct."""
        CertificateTemplateAsset.objects.create(name='test name', asset_file=SimpleUploadedFile(
            'picture1.jpg',
            'file contents!')).save()
        certificate_template_asset = CertificateTemplateAsset.objects.get(id=1)
        self.assertEqual(unicode(certificate_template_asset), "test name")


class TestCertificates(TestCase):
    """Basic setup for certificate tests."""
    def setUp(self):
        super(TestCertificates, self).setUp()
        self.site = Site.objects.create(domain="test", name="test")
        Signatory(name='test name', title='test title', image=SimpleUploadedFile(
            'picture1.jpg',
            'image contents!')).save()
        self.signatory = Signatory.objects.get(id=1)


class TestProgramCertificate(TestCertificates):
    """Test Program Certificate model."""

    def test_unicode_value(self):
        """Test unicode value is correct."""
        program_certificate = ProgramCertificate.objects.create(site=self.site, is_active=True, program_id="123")
        program_certificate.signatories.add(self.signatory)
        self.assertEqual(unicode(program_certificate), '123')


class TestCourseCertificate(TestCertificates):
    """Test Course Certificate model."""

    def setUp(self):
        super(TestCourseCertificate, self).setUp()
        self.course_key = CourseLocator(org='test', course='test', run='test')

    def test_unicode_value(self):
        """Test unicode value is correct."""
        course_certificate = CourseCertificate.objects.create(
            site=self.site, is_active=True, course_id=self.course_key, certificate_type="honor"
        )
        course_certificate.signatories.add(self.signatory)
        self.assertEqual(unicode(course_certificate), unicode(self.course_key) + ", honor")


class TestUserCredential(TestCertificates):
    """Test User Credential model."""

    def setUp(self):
        super(TestUserCredential, self).setUp()
        self.course_key = CourseLocator(org='test', course='test', run='test')
        self.course_certificate = CourseCertificate.objects.create(
            site=self.site, is_active=True, course_id=self.course_key, certificate_type="honor"
        )
        self.course_certificate.signatories.add(self.signatory)

    def test_unicode_value(self):
        """Test unicode value is correct."""
        user_credential = UserCredential.objects.create(username='test_user', credential=self.course_certificate)
        self.assertEqual(unicode(user_credential), 'test_user, awarded')


class TestUserCredentialAttribute(TestCertificates):
    """Test User Credential Attribute model."""

    def setUp(self):
        super(TestUserCredentialAttribute, self).setUp()
        self.course_key = CourseLocator(org='test', course='test', run='test')
        self.course_certificate = CourseCertificate.objects.create(
            site=self.site, is_active=True, course_id=self.course_key, certificate_type="honor"
        )
        self.course_certificate.signatories.add(self.signatory)
        self.user_credential = UserCredential.objects.create(username='test_user', credential=self.course_certificate)

    def test_unicode_value(self):
        """Test unicode value is correct."""
        user_credential_attr = UserCredentialAttribute.objects.create(
            user_credential=self.user_credential, name='grade', namespace="test grade", value="80"
        )
        self.assertEqual(unicode(user_credential_attr), unicode(self.user_credential) + ', test grade, grade')
