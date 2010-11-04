from django.test import TestCase
from lingcod.features import *
from lingcod.features.models import Feature
from lingcod.features.forms import FeatureForm
import os
import shutil
from django.test.client import Client
from django.contrib.auth.models import *
from django.core.urlresolvers import reverse


# used by some of the tests to temporarily create a template file
def create_template(path):
    d = os.path.dirname(__file__)
    dpath = os.path.dirname(os.path.join(d, 'templates', path))
    os.mkdir(dpath)
    path = os.path.join(dpath, 'show.html')
    f = open(path, 'w')
    f.write('h1 />')
    f.close()

def delete_template(path):
    d = os.path.dirname(__file__)
    dpath = os.path.join(d, 'templates')
    path = os.path.join(dpath, path)
    path = os.path.dirname(path)
    if os.path.exists(path):
        shutil.rmtree(path)
        
class TestGetFormClassFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.TestFeatureForm'

class TestFeatureForm(FeatureForm):
    class Meta:
        model = TestGetFormClassFeature

class TestGetFormClassFailFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.TestForm'

class TestForm:
    class Meta:
        model = TestGetFormClassFeature


class FeatureOptionsTest(TestCase):
    
    def test_check_for_subclass(self):
        class NotAFeature:
            pass
        
        with self.assertRaisesRegexp(FeatureConfigurationError, 'subclass'):
            FeatureOptions(NotAFeature)
    
    def test_check_for_inner_class(self):
        class TestFeatureFails(Feature):
            pass
            
        with self.assertRaisesRegexp(FeatureConfigurationError,'not defined'):
            TestFeatureFails.get_options()
            
    def test_must_have_form_class(self):
        class TestFeatureNoForm(Feature):
            class Options:
                pass

        with self.assertRaisesRegexp(FeatureConfigurationError,'form'):
            TestFeatureNoForm.get_options()
    
    def test_must_specify_form_as_string(self):
        class TestFeature(Feature):
            class Options:
                form = FeatureForm

        with self.assertRaisesRegexp(FeatureConfigurationError,'string'):
            TestFeature.get_options()

    def test_slug(self):
        class TestSlugFeature(Feature):
            class Options:
                form = 'lingcod.features.form.FeatureForm'
                
        self.assertEqual(TestSlugFeature.get_options().slug, 'testslugfeature')
    
    def test_default_verbose_name(self):
        class TestDefaultVerboseNameFeature(Feature):
            class Options:
                form = 'lingcod.features.form.FeatureForm'
        
        self.assertEqual(
            TestDefaultVerboseNameFeature.get_options().verbose_name, 
            'TestDefaultVerboseNameFeature')
    
    def test_custom_verbose_name(self):
        class TestCustomVerboseNameFeature(Feature):
            class Options:
                form = 'lingcod.features.form.FeatureForm'
                verbose_name = 'vb-name'
        
        self.assertEqual(
            TestCustomVerboseNameFeature.get_options().verbose_name, 
            'vb-name')
        
    def test_default_show_template(self):
        class TestDefaultShowTemplateFeature(Feature):
            class Options:
                form = 'lingcod.features.form.FeatureForm'
        
        options = TestDefaultShowTemplateFeature.get_options()
        path = options.slug + '/show.html'
        delete_template(path)
        create_template(path)
        self.assertEqual(
            options.get_show_template().name, 
            path)
        delete_template(path)
    
    def test_custom_show_template(self):
        class TestCustomShowTemplateFeature(Feature):
            class Options:
                form = 'lingcod.features.form.FeatureForm'
                show_template = 'location/show.html'
        
        options = TestCustomShowTemplateFeature.get_options()
        path = TestCustomShowTemplateFeature.Options.show_template
        delete_template(path)
        create_template(path)
        self.assertEqual(
            options.get_show_template().name, 
            path)
        delete_template(path)
        
    
    def test_missing_default_show_template(self):
        class TestMissingDefaultShowTemplateFeature(Feature):
            class Options:
                form = 'lingcod.features.form.FeatureForm'
        
        options = TestMissingDefaultShowTemplateFeature.get_options()
        path = options.slug + '/show.html'
        self.assertEqual(
            options.get_show_template().name, 
            'features/show.html')

    def test_missing_custom_show_template(self):
        class TestMissingCustomShowTemplateFeature(Feature):
            class Options:
                form = 'lingcod.features.form.FeatureForm'
                show_template = 'location/show.html'

        options = TestMissingCustomShowTemplateFeature.get_options()
        self.assertEqual(
            options.get_show_template().name, 
            'features/show.html')

    
    def test_get_form_class(self):
        self.assertEqual(
            TestGetFormClassFeature.get_options().get_form_class(),
            TestFeatureForm)
    
    def test_get_form_not_subclass(self):
        with self.assertRaisesRegexp(FeatureConfigurationError, 'subclass'):
            TestGetFormClassFailFeature.get_options().get_form_class()

    def test_json(self):
        pass

# Generic view tests

class TestDeleteFeature(Feature):
    class Options:
        form = 'lingcod.features.form.FeatureForm'
        
register(TestDeleteFeature)
        
class DeleteTest(TestCase):


    def setUp(self):
        self.client = Client()
        self.options = TestDeleteFeature.get_options()
        self.user = User.objects.create_user(
            'resttest', 'resttest@marinemap.org', password='pword')
        self.test_instance = TestDeleteFeature(user=self.user, name="My Name")
        self.test_instance.save()

    def test_delete_not_logged_in(self):
        """
        If user not logged in they can't delete anything
        401 status_code response
        """
        url = self.test_instance.get_absolute_url()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401)

    def test_delete_not_owner(self):
        """
        Don't allow just any old user to delete objects.
        Return 403 Forbidden status code
        """
        other_user = User.objects.create_user(
            'other', 'other@marinemap.org', password='pword')
        self.client.login(username=other_user.username, password='pword')
        url = self.test_instance.get_absolute_url()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_delete_not_owner_but_staff(self):
        """
        Staff users can delete anyone's stuff
        """
        staff_user = User.objects.create_user(
            'staff', 'staff@marinemap.org', password='pword')
        staff_user.is_staff = True
        staff_user.save()
        pk = self.test_instance.pk
        url = self.test_instance.get_absolute_url()
        self.assertEqual(TestDeleteFeature.objects.filter(pk=pk).count(), 1)
        self.client.login(username='staff', password='pword')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TestDeleteFeature.objects.filter(pk=pk).count(), 0)

    def test_delete_authorized(self):
        """
        Users can delete objects that belong to them
        """
        pk = self.test_instance.pk
        self.assertEqual(TestDeleteFeature.objects.filter(pk=pk).count(), 1)
        url = self.test_instance.get_absolute_url()
        self.client.login(username='resttest', password='pword')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TestDeleteFeature.objects.filter(pk=pk).count(), 0)
        

class CreateFormTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.CreateFormTestForm'

class CreateFormTestForm(FeatureForm):
    class Meta:
        model = CreateFormTestFeature

register(CreateFormTestFeature)

class CreateFormTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'resttest', 'resttest@marinemap.org', password='pword')
        self.options = CreateFormTestFeature.get_options()

    def test_user_not_logged_in(self):
        """
        Can't create stuff without being logged in.
        """
        response = self.client.get(self.options.get_create_form())
        self.assertEqual(response.status_code, 401)

    def test_get_form(self):
        """
        Returns a form that can be displayed on the client.
        """
        self.client.login(username='resttest', password='pword')
        response = self.client.get(self.options.get_create_form())
        self.assertEqual(response.status_code, 200)


class CreateTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.CreateTestForm'

class CreateTestForm(FeatureForm):
    class Meta:
        model = CreateTestFeature

register(CreateTestFeature)


class CreateTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'resttest', 'resttest@marinemap.org', password='pword')
        self.options = CreateTestFeature.get_options()
        self.create_url = self.options.get_create_form()

    def test_submit_not_authenticated(self):
        response = self.client.post(self.create_url, 
            {'name': "My Test", 'user': 1})
        self.assertEqual(response.status_code, 401)

    def test_submit_invalid_form(self):
        old_count = CreateTestFeature.objects.count()
        self.client.login(username='resttest', password='pword')
        response = self.client.post(self.create_url, {'name': ''})
        self.assertEqual(response.status_code, 400)
        self.assertTrue(old_count == CreateTestFeature.objects.count())
        self.assertNotEqual(
            response.content.find('This field is required.'), -1)

    def test_submit_valid_form(self):
        old_count = CreateTestFeature.objects.count()
        self.client.login(username='resttest', password='pword')
        response = self.client.post(self.create_url, {'name': "My Test"})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(old_count < CreateTestFeature.objects.count())
        inst = CreateTestFeature.objects.get(name='My Test')
        self.assertTrue(
            response['Location'].count(inst.get_absolute_url()) == 1)

    def test_cannot_hack_user_field(self):
        other_user = User.objects.create_user(
            'other', 'other@marinemap.org', password='pword')
        old_count = CreateTestFeature.objects.count()
        self.client.login(username='resttest', password='pword')
        response = self.client.post(self.create_url, 
            {'name': "My Test Hack Test", 'user': other_user.pk})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(old_count < CreateTestFeature.objects.count())
        new_instance = CreateTestFeature.objects.get(name='My Test Hack Test')
        self.assertNotEqual(new_instance.user, other_user)

class UpdateFormTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.UpdateFormTestForm'

class UpdateFormTestForm(FeatureForm):
    class Meta:
        model = UpdateFormTestFeature

register(UpdateFormTestFeature)

class UpdateFormTest(TestCase):

    def setUp(self):
        self.options = UpdateFormTestFeature.get_options()
        self.client = Client()
        self.user = User.objects.create_user(
            'resttest', 'resttest@marinemap.org', password='pword')
        self.test_instance = UpdateFormTestFeature(
            user=self.user, name="My Name")
        self.test_instance.save()
        self.update_form_url = self.options.get_update_form(
            self.test_instance.pk)

    def test_get_form(self):
        self.client.login(username='resttest', password='pword')
        response = self.client.get(self.update_form_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.content.find('My Name'), -1)

    def test_not_logged_in(self):
        response = self.client.get(self.update_form_url)
        self.assertEqual(response.status_code, 401)

    def test_not_owner(self):
        other_user = User.objects.create_user(
            'other', 'other@marinemap.org', password='pword')
        self.client.login(username='other', password='pword')
        response = self.client.get(self.update_form_url)
        self.assertEqual(response.status_code, 403)

    def test_not_owner_but_staff(self):
        staff_user = User.objects.create_user(
            'staff', 'other@marinemap.org', password='pword')
        staff_user.is_staff = True
        staff_user.save()
        self.client.login(username='staff', password='pword')
        response = self.client.get(self.update_form_url)
        self.assertEqual(response.status_code, 200)

    def test_not_found(self):
        self.client.login(username='resttest', password='pword')
        response = self.client.get(self.options.get_update_form(30000000000))
        self.assertEqual(response.status_code, 404)


class UpdateTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.UpdateTestForm'

class UpdateTestForm(FeatureForm):
    class Meta:
        model = UpdateTestFeature

register(UpdateTestFeature)

class UpdateTest(TestCase):

    def setUp(self):
        self.options = UpdateTestFeature.get_options()
        self.client = Client()
        self.user = User.objects.create_user(
            'resttest', 'resttest@marinemap.org', password='pword')
        self.test_instance = UpdateTestFeature(user=self.user, name="My Name")
        self.test_instance.save()
        self.update_form_url = self.options.get_update_form(
            self.test_instance.pk)
        self.instance_url = self.test_instance.get_absolute_url()

    def test_post(self):
        self.client.login(username='resttest', password='pword')
        response = self.client.post(self.instance_url, {
            'name': 'My New Name',
        })
        self.assertEqual(response.status_code, 200)

    def test_post_validation_error(self):
        self.client.login(username='resttest', password='pword')
        response = self.client.post(self.instance_url, {
            'name': '',
        })
        self.assertEqual(response.status_code, 400)

    def test_post_not_logged_in(self):
        response = self.client.post(self.instance_url, {
            'name': 'My New Name',
        })
        self.assertEqual(response.status_code, 401)

    def test_post_not_owner(self):
        other_user = User.objects.create_user('other', 'other@marinemap.org', password='pword')
        self.client.login(username='other', password='pword')
        response = self.client.post(self.instance_url, {
            'name': 'My New Name',
        })
        self.assertEqual(response.status_code, 403)

    def test_post_not_owner_but_staff(self):
        other_user = User.objects.create_user('other', 'other@marinemap.org', password='pword')
        other_user.is_staff = True
        other_user.save()
        self.client.login(username='other', password='pword')
        response = self.client.post(self.instance_url, {
            'name': 'My New Name',
        })
        self.assertEqual(response.status_code, 200)

    def test_not_found(self):
        self.client.login(username='resttest', password='pword')
        response = self.client.post(self.options.get_resource(10000000), {
            'name': 'My New Name',
        })
        self.assertEqual(response.status_code, 404)

    def test_cannot_hack_user_field(self):
        other_user = User.objects.create_user('other', 'other@marinemap.org', password='pword')
        self.client.login(username='resttest', password='pword')
        response = self.client.post(self.instance_url, {
            'name': 'My New Name',
            'user': other_user.pk,
        })
        self.assertEqual(response.status_code, 200)
        edited_instance = UpdateTestFeature.objects.get(pk=self.test_instance.pk)
        self.assertNotEqual(edited_instance.user, other_user)

def valid_single_select_view(request, instance):
    pass

def invalid_single_select_view(request, pk):
    pass

def invalid_multiple_select_view(request, fail):
    pass

def valid_multiple_select_view(request, instances):
    pass

class LinkViewValidationTest(TestCase):
    
    def test_single_select_view_requires_instance_argument(self):
        # Must accept at least a second argument for the instance
        with self.assertRaises(FeatureConfigurationError):
            link = alternate(
                'test title',
                'lingcod.features.tests.invalid_single_select_view')
                
        # Accepts the instance argument
        link = alternate('test title',
            'lingcod.features.tests.valid_single_select_view')
        self.assertIsInstance(link, Link)
    
    def test_multiple_select_view_requires_instance_argument(self):
        # Must accept at least a second argument for the instances
        with self.assertRaises(FeatureConfigurationError):
            link = alternate('test title',
                'lingcod.features.tests.invalid_multiple_select_view', 
                select='multiple')

        # Accepts the instance argument
        link = alternate('test title',
            'lingcod.features.tests.valid_multiple_select_view', 
            select='multiple')
        self.assertIsInstance(link, Link)
        
    def test_check_extra_kwargs_allowed(self):
        pass
        # TODO: Test that Link validates extra_kwargs option is compatible 
        # with the view

class LinkTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.LinkTestFeatureForm'
        links = (
            alternate('Single Select View',
                'lingcod.features.tests.valid_single_select_view',  
                type="application/shapefile"),
                
            alternate('Spreadsheet of all Features',
                'lingcod.features.tests.valid_multiple_select_view',
                type="application/xls", 
                select='multiple single')
        )
        
class LinkTestFeatureForm(FeatureForm):
    class Meta:
        model = LinkTestFeature

register(LinkTestFeature)

class LinkTest(TestCase):
    
    def setUp(self):
        self.options = LinkTestFeature.get_options()
        self.client = Client()
        self.user = User.objects.create_user(
            'resttest', 'resttest@marinemap.org', password='pword')
        self.test_instance = LinkTestFeature(user=self.user, name="My Name")
        self.test_instance.save()
        self.update_form_url = self.options.get_update_form(
            self.test_instance.pk)
        self.instance_url = self.test_instance.get_absolute_url()
    
    def test_get_links(self):
        links = LinkTestFeature.get_options().links
        link = links[0]
        link2 = links[1]
        self.assertIsInstance(link, Link)
        self.assertEqual('Single Select View', link.title)
        self.assertEqual('single', link.select)
        self.assertEqual('multiple single', link2.select)
    
    def test_links_registered(self):
        options = LinkTestFeature.get_options()
        links = options.links
        link = links[0]
        link2 = links[1]
        # Check to see that the Feature Class was registered at all
        self.client.login(username='resttest', password='pword')
        response = self.client.get(self.options.get_create_form())
        self.assertEqual(response.status_code, 200)
        # Check that both links have urls
        path = link.reverse(self.test_instance)
        response = self.client.get(path)
        self.assertRegexpMatches(response.content, r'My Name')