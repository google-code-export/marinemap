from django.test import TestCase
from lingcod.features import *
from lingcod.features.models import Feature, PointFeature, LineFeature, PolygonFeature, FeatureCollection
from lingcod.features.forms import FeatureForm
from lingcod.sharing.utils import get_shareables, share_object_with_group
from lingcod.common.utils import kml_errors
import os
import shutil
from django.test.client import Client
from django.contrib.auth.models import *
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden


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

@register        
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
    
# Generic view tests

@register
class TestDeleteFeature(Feature):
    class Options:
        form = 'lingcod.features.form.FeatureForm'
        
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
        

@register
class CreateFormTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.CreateFormTestForm'

class CreateFormTestForm(FeatureForm):
    class Meta:
        model = CreateFormTestFeature

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

@register
class CreateTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.CreateTestForm'

class CreateTestForm(FeatureForm):
    class Meta:
        model = CreateTestFeature


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

@register
class UpdateFormTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.UpdateFormTestForm'

class UpdateFormTestForm(FeatureForm):
    class Meta:
        model = UpdateFormTestFeature

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

@register
class UpdateTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.UpdateTestForm'

class UpdateTestForm(FeatureForm):
    class Meta:
        model = UpdateTestFeature

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
    return HttpResponse(instance.name)

def invalid_single_select_view(request, pk):
    pass

def invalid_multiple_select_view(request, fail):
    pass

def valid_multiple_select_view(request, instances):
    return HttpResponse(', '.join([i.name for i in instances]))

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

@register
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
                select='multiple single'),
            
            edit('Edit single feature',
                'lingcod.features.tests.valid_single_select_view'
            ),
            
            edit_form('Edit multiple features',
                'lingcod.features.tests.valid_multiple_select_view',
                select='multiple single'
            ),
        )

class LinkTestFeatureForm(FeatureForm):
    class Meta:
        model = LinkTestFeature


class LinkTest(TestCase):
    
    def setUp(self):
        self.options = LinkTestFeature.get_options()
        self.client = Client()
        self.user = User.objects.create_user(
            'resttest', 'resttest@marinemap.org', password='pword')
        self.other_user = User.objects.create_user(
            'other', 'other@marinemap.org', password='pword')
        self.test_instance = LinkTestFeature(user=self.user, name="My Name")
        self.test_instance.save()
        self.update_form_url = self.options.get_update_form(
            self.test_instance.pk)
        self.instance_url = self.test_instance.get_absolute_url()
        self.i2 = LinkTestFeature(user=self.user, name="I2")
        self.i2.save()
        
    
    def test_get_links(self):
        links = LinkTestFeature.get_options().links
        link = links[2]
        link2 = links[3]
        self.assertIsInstance(link, Link)
        self.assertEqual('Single Select View', link.title)
        self.assertEqual('single', link.select)
        self.assertEqual('multiple single', link2.select)
    
    def test_links_registered(self):
        options = LinkTestFeature.get_options()
        links = options.links
        link = links[2]
        link2 = links[3]
        # Check to see that the Feature Class was registered at all
        self.client.login(username='resttest', password='pword')
        response = self.client.get(self.options.get_create_form())
        self.assertEqual(response.status_code, 200)
        # Check that both links have urls
        path = link.reverse(self.test_instance)
        response = self.client.get(path)
        self.assertRegexpMatches(response.content, r'My Name')
        path = link2.reverse([self.test_instance, self.i2])
        response = self.client.get(path)
        self.assertRegexpMatches(response.content, r'My Name, I2')
        
    def test_401_response(self):
        """Should not be able to perform editing actions without login.
        """
        links = self.options.links
        response = self.client.post(links[4].reverse(self.test_instance))
        self.assertEqual(response.status_code, 401,response.content)
        response = self.client.get(links[5].reverse(self.test_instance))
        self.assertEqual(response.status_code, 401)
        self.client.login(username='resttest', password='pword')
        response = self.client.get(links[5].reverse(self.test_instance))
        self.assertEqual(response.status_code, 200)        
    
    def test_cant_GET_edit_links(self):
        """For links of rel=edit, a post request should be required.
        """
        links = self.options.links
        self.client.login(username='resttest', password='pword')
        response = self.client.get(links[4].reverse(self.test_instance))
        self.assertEqual(response.status_code, 405,response.content)
        self.assertEqual(response['Allow'], 'POST')
        
    def test_403_response(self):
        """Should not be able to edit shapes a user doesn't own.
        """
        links = self.options.links
        self.client.login(username='other', password='pword')
        response = self.client.get(links[5].reverse(self.test_instance))
        self.assertEqual(response.status_code, 403)        
        
    
    def test_403_response_multiple_instances(self):
        """Should not be able to edit shapes a user doesn't own. Test to make
        sure every feature in a request is checked.
        """
        links = self.options.links
        self.client.login(username='other', password='pword')
        inst = LinkTestFeature(user=self.other_user, 
            name="Other User's feature")
        inst.save()
        response = self.client.get(
            links[5].reverse([inst, self.test_instance]))
        self.assertEqual(response.status_code, 403, response.content)
        
    def test_404_response(self):
        links = self.options.links
        self.client.login(username='resttest', password='pword')
        inst = LinkTestFeature(user=self.user, 
            name="feature")
        inst.save()
        path = links[5].reverse([inst, self.test_instance])
        inst.delete()
        response = self.client.get(path)
        self.assertEqual(response.status_code, 404)

def multi_select_view(request, instances):
    return HttpResponse(', '.join([i.name for i in instances]))

@register
class GenericLinksTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.GenericLinksTestForm'
        links = (
            alternate('Generic Link',
                'lingcod.features.tests.multi_select_view',  
                type="application/shapefile",
                select='multiple single'),
            alternate('Non-Generic Link',
                'lingcod.features.tests.multi_select_view',  
                type="application/shapefile",
                select='multiple single'),
        )

class GenericLinksTestForm(FeatureForm):
    class Meta:
        model = GenericLinksTestFeature


@register
class OtherGenericLinksTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.OtherGenericLinksTestForm'
        links = (
            alternate('Generic Link',
                'lingcod.features.tests.multi_select_view',  
                type="application/shapefile",
                select='multiple single'),
        )


class OtherGenericLinksTestForm(FeatureForm):
    class Meta:
        model = OtherGenericLinksTestFeature

@register
class LastGenericLinksTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.GenericLinksTestForm'
        links = (
            alternate('Different Name',
                'lingcod.features.tests.multi_select_view',  
                type="application/shapefile",
                select='multiple single'),

        )

class GenericLinksTest(TestCase):
    
    # Note that links[2] will be the first generic link in the list
    # ... the first two links are KML and Copy which are automatically created
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'resttest', 'resttest@marinemap.org', password='pword')
        self.generic_instance = GenericLinksTestFeature(user=self.user, 
            name="Generic")
        self.other_instance = OtherGenericLinksTestFeature(user=self.user, 
            name="Other")
        self.last_instance = LastGenericLinksTestFeature(user=self.user, 
            name="Last")
        self.generic_instance.save()
        self.other_instance.save()
        self.last_instance.save()
    
    def test_generic_links_reused_by_create_link(self):
        """Test that the calls to lingcod.features.create_link return 
        references to generic links when appropriate."""
        self.assertEqual(GenericLinksTestFeature.get_options().links[2], 
            OtherGenericLinksTestFeature.get_options().links[2])
        self.assertNotEqual(
            OtherGenericLinksTestFeature.get_options().links[2],
            LastGenericLinksTestFeature.get_options().links[2])
            
    def test_generic_links_work(self):
        """Test that a generic view can recieve a request related to more than
        one feature class."""
        link = GenericLinksTestFeature.get_options().links[2]
        path = link.reverse([self.generic_instance, self.other_instance])
        self.client.login(username='resttest', password='pword')
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertRegexpMatches(response.content, r'Generic')
        self.assertRegexpMatches(response.content, r'Other')
        
    def test_generic_links_deny_unconfigured_models(self):
        """Generic links shouldn't work for any model, only those that have 
        the link configured in their Options class."""
        link = GenericLinksTestFeature.get_options().links[2]
        path = link.reverse([self.generic_instance, self.last_instance])
        self.client.login(username='resttest', password='pword')
        response = self.client.get(path)
        self.assertEqual(response.status_code, 400,response.content)
        self.assertRegexpMatches(response.content, r'GenericLinksTestFeature')
        self.assertRegexpMatches(response.content, 
            r'OtherGenericLinksTestFeature')



def delete_w_contents(request, instances):
    return HttpResponse('Deleted')

def habitat_spreadsheet(request, instance):
    return HttpReponse('Report Contents')

def viewshed_map(request, instance):
    return HttpResponse('image')

def kml(request, instances):
    print instances
    return HttpResponse('<kml />')
    
# Lets use the following as a canonical example of how to use all the features
# of this framework (will be kept up to date as api changes):
        
DESIGNATION_CHOICES = (
    ('R', 'Reserve'), 
    ('P', 'Park'),
    ('C', 'Conservation Area')
)

@register
class TestMpa(PolygonFeature):
    designation = models.CharField(max_length=1, choices=DESIGNATION_CHOICES)
    class Options:
        share = True
        verbose_name = 'Marine Protected Area'
        form = 'lingcod.features.tests.MpaForm'
        manipulators = [ 'lingcod.manipulators.tests.TestManipulator' ]
        optional_manipulators = [ 'lingcod.manipulators.manipulators.ClipToGraticuleManipulator' ]
        links = (
            related('Habitat Spreadsheet',
                'lingcod.features.tests.habitat_spreadsheet',
                select='single',
                type='application/xls'
            ),
            alternate('Export KML',
                'lingcod.features.tests.kml',
                select='multiple single'
            )
        )
        
class MpaForm(FeatureForm):
    class Meta:
        model = TestMpa

@register
class Folder(FeatureCollection):
    
    def copy(self, user):
        copy = super(Folder, self).copy(user)
        copy.name = copy.name.replace(' (copy)', '-Copy')
        copy.save()
        return copy
    
    class Options:
        form = 'lingcod.features.tests.FolderForm'
        share=True
        valid_children = (
            'lingcod.features.tests.TestMpa', 
            'lingcod.features.tests.Folder', 
            'lingcod.features.tests.RenewableEnergySite')
        links = (
            edit('Delete folder and contents',
                'lingcod.features.tests.delete_w_contents',
                select='single multiple',
                confirm="""
                Are you sure you want to delete this folder and it's contents? 
                This action cannot be undone.
                """
            ),
            alternate('Export KML',
                'lingcod.features.tests.kml',
                select='multiple single'
            )
        )

class FolderForm(FeatureForm):
    class Meta:
        model = Folder

TYPE_CHOICES = (
    ('W', 'Wind'),
    ('H', 'Hydrokinetic'),
)

@register
class RenewableEnergySite(PolygonFeature):
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    class Options:
        verbose_name = 'Renewable Energy Site'
        form = 'lingcod.features.tests.RenewableEnergySiteForm'
        links = (
            related('Viewshed Map',
                'lingcod.features.tests.viewshed_map',
                select='single',
                type='image/png'
            ),
            alternate('Export KML',
                'lingcod.features.tests.kml',
                select='multiple single'
            )
        )

class RenewableEnergySiteForm(FeatureForm):
    class Meta:
        model = RenewableEnergySite
        
@register
class Pipeline(LineFeature):
    type = models.CharField(max_length=30,default='')
    diameter = models.FloatField(null=True)
    class Options:
        verbose_name = 'Pipeline'
        form = 'lingcod.features.tests.PipelineForm'

class PipelineForm(FeatureForm):
    class Meta:
        model = Pipeline

@register
class Shipwreck(PointFeature):
    incident = models.CharField(max_length=100,default='')
    class Options:
        verbose_name = 'Shipwreck'
        form = 'lingcod.features.tests.ShipwreckForm'

class ShipwreckForm(FeatureForm):
    class Meta:
        model = Shipwreck


class JsonSerializationTest(TestCase):
    
    def test_workspace(self):
        pass
        
class CopyTest(TestCase):
    
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            'resttest', 'resttest@marinemap.org', password='pword')
        self.other_user = User.objects.create_user(
            'othertest', 'othertest@marinemap.org', password='pword')
        self.group1 = Group.objects.create(name="Test Group 1")
        self.group1.save()
        self.user.groups.add(self.group1)
        self.other_user.groups.add(self.group1)
        shareables = get_shareables()
        self.group1.permissions.add(shareables['testmpa'][1])

        self.mpa = TestMpa(user=self.user, name="My Mpa")
        self.folder = Folder(user=self.user, name="My Folder")
        self.folder.save()
        self.mpa.save()
    
    def test_login_required(self):
        for link in self.mpa.get_options().links:
            if link.title == 'Copy':
                copy_link = link
                break
        self.assertEqual(Link, getattr(link, '__class__', None))
        response = self.client.post(link.reverse([self.mpa]))
        # commenting out until sharing is supported on feature classes
        # self.assertEqual(response.status_code, 401)
            
    def test_copy(self):
        self.client.login(username='resttest', password='pword')
        for link in self.mpa.get_options().links:
            if link.title == 'Copy':
                copy_link = link
                break
        self.assertEqual(Link, getattr(link, '__class__', None))
        response = self.client.post(link.reverse([self.mpa]))
        self.assertRegexpMatches(response.content, r'(copy)')
        self.assertRegexpMatches(response['X-MarineMap-Select'], 
            r'features_testmpa_\d')
    
    def test_copy_multiple_and_custom_copy_method(self):
        self.client.login(username='resttest', password='pword')
        for link in self.mpa.get_options().links:
            if link.title == 'Copy':
                copy_link = link
                break
        self.assertEqual(Link, getattr(link, '__class__', None))
        path = link.reverse([self.mpa, self.folder])
        response = self.client.post(path)
        self.assertRegexpMatches(response.content, r'(copy)')
        self.assertRegexpMatches(response.content, r'Folder-Copy')
        self.assertRegexpMatches(response['X-MarineMap-Select'], 
            r'features_testmpa_\d+ features_folder_\d+')
    
    def test_other_users_can_copy_if_shared(self):
        share_object_with_group(self.mpa, self.group1) 
        self.client.login(username='othertest', password='pword')
        for link in self.mpa.get_options().links:
            if link.title == 'Copy':
                copy_link = link
                break
        self.assertEqual(Link, getattr(link, '__class__', None))
        response = self.client.post(link.reverse([self.mpa]))
        self.assertRegexpMatches(response.content, r'(copy)')
        self.assertRegexpMatches(response['X-MarineMap-Select'], 
            r'features_testmpa_\d')


class SpatialTest(TestCase):

    def setUp(self):
        from django.contrib.gis.geos import GEOSGeometry 
        from django.conf import settings
        self.client = Client()
        self.user = User.objects.create_user(
            'resttest', 'resttest@marinemap.org', password='pword')
        self.client.login(username='resttest', password='pword')
        
        g3 = GEOSGeometry('SRID=4326;POINT(-120.45 34.32)')
        g3.transform(settings.GEOMETRY_DB_SRID)
        self.wreck = Shipwreck(user=self.user, name="Nearby Wreck", geometry_final=g3)
        self.wreck.save()

        g2 = GEOSGeometry('SRID=4326;LINESTRING(-120.42 34.37, -121.42 33.37)')
        g2.transform(settings.GEOMETRY_DB_SRID)
        self.pipeline = Pipeline(user=self.user, name="My Pipeline", geometry_final=g2)
        self.pipeline.save()

        g1 = GEOSGeometry('SRID=4326;POLYGON((-120.42 34.37, -119.64 34.32, -119.63 34.12, -120.44 34.15, -120.42 34.37))')
        g1.transform(settings.GEOMETRY_DB_SRID)
        self.mpa = TestMpa(user=self.user, name="My Mpa", geometry_orig=g1) 
        # geometry_final will be set with manipulator
        self.mpa.save()

    def test_feature_types(self):
        self.assertTrue(isinstance(self.wreck, PointFeature))
        self.assertEqual(self.wreck.geometry_final.geom_type,'Point')

        self.assertTrue(isinstance(self.pipeline, LineFeature))
        self.assertEqual(self.pipeline.geometry_final.geom_type,'LineString')

        self.assertTrue(isinstance(self.mpa, PolygonFeature))
        self.assertEqual(self.mpa.geometry_final.geom_type,'Polygon')

    def test_point_defaultkml_url(self):
        url = [link.reverse(self.wreck) for link in self.wreck.get_options().links if link.title == "KML"][0]
        response = self.client.get(url)
        errors = kml_errors(response.content)
        self.assertFalse(errors,"invalid KML %s" % str(errors))
        
    def test_line_defaultkml_url(self):
        url = [link.reverse(self.pipeline) for link in self.pipeline.get_options().links if link.title == "KML"][0]
        response = self.client.get(url)
        errors = kml_errors(response.content)
        self.assertFalse(errors,"invalid KML %s" % str(errors))

    def test_polygon_defaultkml_url(self):
        url = [link.reverse(self.mpa) for link in self.mpa.get_options().links if link.title == "KML"][0]
        response = self.client.get(url)
        errors = kml_errors(response.content)
        self.assertFalse(errors,"invalid KML %s" % str(errors))


class CollectionTest(TestCase):
    
    def setUp(self):
        self.client = Client()

        self.user1 = User.objects.create_user(
            'user1', 'resttest@marinemap.org', password='pword')
        self.user2 = User.objects.create_user(
            'user2', 'othertest@marinemap.org', password='pword')
        self.group1 = Group.objects.create(name="Test Group 1")
        self.group1.save()
        self.user1.groups.add(self.group1)
        self.user2.groups.add(self.group1)
        shareables = get_shareables()
        self.group1.permissions.add(shareables['testmpa'][1])
        self.group1.permissions.add(shareables['folder'][1])

        self.mpa1 = TestMpa(user=self.user1, name="My Mpa")
        self.mpa1.save()
        self.mpa2 = TestMpa(user=self.user1, name="My Mpa 2")
        self.mpa2.save()
        self.folder1 = Folder(user=self.user1, name="My Folder")
        self.folder1.save()
        self.folder2 = Folder(user=self.user1, name="My Folder2")
        self.folder2.save()

    def test_add_remove_at_feature_level(self):
        self.mpa1.add_to_collection(self.folder1)
        self.assertEqual(self.mpa1.collection, self.folder1)
        self.assertTrue(self.mpa1 in self.folder1.feature_set())

        self.mpa1.remove_from_collection()
        self.assertEqual(self.mpa1.collection, None)
        self.assertTrue(self.mpa1 not in self.folder1.feature_set())
        
    def test_add_remove_at_collection_level(self):
        self.folder1.add(self.mpa1)
        self.assertEqual(self.mpa1.collection, self.folder1)
        self.assertTrue(self.mpa1 in self.folder1.feature_set())

        self.folder1.remove(self.mpa1)
        self.assertEqual(self.mpa1.collection, None)
        self.assertTrue(self.mpa1 not in self.folder1.feature_set())

    def test_feature_set(self):
        """
        When checking which mpas belong to folder1 we can:
        * look only at immediate children
        * look for children of a given feature class
        * look recursively through all containers

         folder1
          |- mpa1
          |- folder2
              | - mpa2
        """
        self.folder1.add(self.mpa1)
        self.folder2.add(self.mpa2)
        self.folder1.add(self.folder2)

        direct_children = self.folder1.feature_set(recurse=False)
        self.assertEqual(len(direct_children), 2)
        self.assertTrue(self.mpa1 in direct_children)
        self.assertTrue(self.folder2 in direct_children)
        self.assertTrue(self.mpa2 not in direct_children)

        direct_mpa_children = self.folder1.feature_set(recurse=False,feature_classes=[TestMpa])
        self.assertEqual(len(direct_mpa_children), 1)
        self.assertTrue(self.mpa1 in direct_mpa_children)
        self.assertTrue(self.folder2 not in direct_mpa_children)
        self.assertTrue(self.mpa2 not in direct_mpa_children)

        recursive_mpa_children = self.folder1.feature_set(recurse=True,feature_classes=[TestMpa])
        self.assertEqual(len(recursive_mpa_children), 2)
        self.assertTrue(self.mpa1 in recursive_mpa_children)
        self.assertTrue(self.folder2 not in recursive_mpa_children)
        self.assertTrue(self.mpa2 in recursive_mpa_children)

    def test_deep_recursion(self):
        """
         folder1
          |- mpa1
          |- folder2
              | - mpa2
              | - folder3
                   |- mpa3
                   |- folder4
                       |- mpa4
                       |- mpa5
        """
        mpa3 = TestMpa(user=self.user1, name="My Mpa")
        mpa3.save()
        mpa4 = TestMpa(user=self.user1, name="My Mpa 2")
        mpa4.save()
        mpa5 = TestMpa(user=self.user1, name="My Mpa 2")
        mpa5.save()
        folder3 = Folder(user=self.user1, name="My Folder")
        folder3.save()
        folder4 = Folder(user=self.user1, name="My Folder2")
        folder4.save()

        self.folder1.add(self.mpa1)
        self.folder2.add(self.mpa2)
        self.folder1.add(self.folder2)
        self.folder2.add(folder3)
        folder3.add(folder4)
        folder3.add(mpa3)
        folder4.add(mpa4)
        folder4.add(mpa5)

        recursive_mpa_children = self.folder1.feature_set(recurse=True,feature_classes=[TestMpa])
        self.assertEqual(len(recursive_mpa_children), 5)
        self.assertTrue(self.mpa1 in recursive_mpa_children)
        self.assertTrue(mpa5 in recursive_mpa_children)
        self.assertTrue(folder4 not in recursive_mpa_children)

        recursive_children = self.folder1.feature_set(recurse=True)
        self.assertEqual(len(recursive_children), 8)
        self.assertTrue(self.mpa1 in recursive_children)
        self.assertTrue(mpa5 in recursive_children)
        self.assertTrue(folder4 in recursive_children)


    def test_add_invalid_child_feature(self):
        pass

    def test_validate_bad_child_class_string(self):
        pass

    def test_share_collection_view_children(self):
        """
        If folder1 is shared, user2 should see mpa1, folder2 and mpa2
        """
        pass

    def test_copy_feature_collection(self):
        """ 
        folder1 copied to folder1-copy
        make sure it contains mpa1-copy, mpa2-copy and folder2-copy
        """
        pass
