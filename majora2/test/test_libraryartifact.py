from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.conf import settings

from majora2 import models
from tatl import models as tmodels
from majora2.test.test_basic_api import OAuthAPIClientBase

user_anonymous_sample_id = "%s-%s" % (settings.ANON_PREFIXES[0] if settings.ANON_PREFIXES else "TEST", "00000001")
user_anonymous_sample_id_2 = "%s-%s" % (settings.ANON_PREFIXES[0] if settings.ANON_PREFIXES else "TEST", "00000002")                     

class OAuthLibraryArtifactTest(OAuthAPIClientBase):
    def setUp(self):
        super().setUp()

        self.endpoint = reverse("api.artifact.library.add")
        self.scope = "majora2.add_biosampleartifact majora2.add_libraryartifact majora2.add_librarypoolingprocess majora2.change_biosampleartifact majora2.change_libraryartifact majora2.change_librarypoolingprocess"
        self.token = self._get_token(self.scope)

        self.empty_bio_endpoint = reverse("api.artifact.biosample.addempty")
        self.empty_bio_scope = "majora2.force_add_biosampleartifact majora2.add_biosampleartifact majora2.change_biosampleartifact majora2.add_biosourcesamplingprocess majora2.change_biosourcesamplingprocess"
        self.empty_bio_token = self._get_token(self.empty_bio_scope)

    def test_add_basic_library_ok(self):
        lib_count = models.LibraryArtifact.objects.count()

        # Biosample needs to exist to add a library (without forcing)
        bs = models.BiosampleArtifact(central_sample_id="HOOT-00001", dice_name="HOOT-00001")
        bs.save()

        library_name = "HOOT-LIB-1"
        payload = {
            "biosamples": [
                {
                    "central_sample_id": bs.dice_name,
                    "library_source": "VIRAL_RNA",
                    "library_selection": "PCR",
                    "library_strategy": "AMPLICON",
                }
            ],
            "library_layout_config": "SINGLE",
            "library_name": library_name,
            "library_seq_kit": "KIT",
            "library_seq_protocol": "PROTOCOL",
            "username": "OAUTH",
            "token": "OAUTH"
        }

        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        self.assertEqual(models.LibraryArtifact.objects.count(), lib_count + 1)
        assert models.LibraryArtifact.objects.filter(dice_name=library_name).count() == 1

        library = models.LibraryArtifact.objects.get(dice_name=library_name)
        assert library.layout_config == payload.get("library_layout_config")
        assert library.layout_read_length == payload.get("library_layout_read_length")
        assert library.layout_insert_length == payload.get("library_layout_insert_length")
        assert library.seq_kit == payload.get("library_seq_kit")
        assert library.seq_protocol == payload.get("library_seq_protocol")

    def test_add_library_twice_no_update(self):
        # Biosample needs to exist to add a library (without forcing)
        bs = models.BiosampleArtifact(central_sample_id="HOOT-00001", dice_name="HOOT-00001")
        bs.save()

        library_name = "HOOT-LIB-1"
        payload = {
            "biosamples": [
                {
                    "central_sample_id": bs.dice_name,
                    "library_source": "VIRAL_RNA",
                    "library_selection": "PCR",
                    "library_strategy": "AMPLICON",
                }
            ],
            "library_layout_config": "SINGLE",
            "library_name": library_name,
            "library_seq_kit": "KIT",
            "library_seq_protocol": "PROTOCOL",
            "username": "OAUTH",
            "token": "OAUTH"
        }

        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        library = models.LibraryArtifact.objects.get(dice_name=library_name)

        # Confirm CREATED verb
        j = response.json()
        tatl = tmodels.TatlRequest.objects.filter(response_uuid=j["request"]).first()
        self.assertIsNotNone(tatl)
        self.assertEqual(tatl.verbs.count(), 2)
        expected_verbs = [
            ("CREATE", library),
            ("UPDATE", bs),
        ]
        for verb in tatl.verbs.all():
            self.assertIn( (verb.verb, verb.content_object), expected_verbs )

        # Add library again
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        # Confirm no UPDATE verb
        j = response.json()
        tatl = tmodels.TatlRequest.objects.filter(response_uuid=j["request"]).first()
        self.assertIsNotNone(tatl)
        self.assertEqual(tatl.verbs.count(), 0)

    def test_update_library(self):
        # Biosample needs to exist to add a library (without forcing)
        bs = models.BiosampleArtifact(central_sample_id="HOOT-00001", dice_name="HOOT-00001")
        bs.save()

        library_name = "HOOT-LIB-1"
        payload = {
            "biosamples": [
                {
                    "central_sample_id": bs.dice_name,
                    "library_source": "VIRAL_RNA",
                    "library_selection": "PCR",
                    "library_strategy": "AMPLICON",
                }
            ],
            "library_layout_config": "SINGLE",
            "library_name": library_name,
            "library_seq_kit": "KIT",
            "library_seq_protocol": "PROTOCOL",
            "username": "OAUTH",
            "token": "OAUTH"
        }

        # Create
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        payload["library_seq_kit"] = "NEWKIT"
        payload["library_seq_protocol"] = "NEWPROTOCOL"

        # Update
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        library = models.LibraryArtifact.objects.get(dice_name=library_name)

        # Assert changes
        assert library.seq_kit == payload.get("library_seq_kit")
        assert library.seq_protocol == payload.get("library_seq_protocol")

        # Confirm UPDATE verb
        j = response.json()
        tatl = tmodels.TatlRequest.objects.filter(response_uuid=j["request"]).first()
        self.assertIsNotNone(tatl)
        self.assertEqual(tatl.verbs.count(), 1)
        expected_verbs = [
            ("UPDATE", library),
        ]
        for verb in tatl.verbs.all():
            self.assertIn( (verb.verb, verb.content_object), expected_verbs )


    def test_m59_add_library_bad_biosamples_key(self):
        lib_count = models.LibraryArtifact.objects.count()

        library_name = "HOOT-LIB-1"
        payload = {
            "biosamples": { "central_sample_id": "HOOT-00001" },
            "library_name": library_name,
            "username": "OAUTH",
            "token": "OAUTH"
        }

        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertIn("'biosamples' appears malformed", "".join(j["messages"]))


    def test_race_condition_err_msg(self):

        library_name = "HOOT-LIB-1"
        models.LibraryArtifact(
            dice_name=library_name,
        ).save() # force add a library without a created process

        payload = {
            "biosamples": [
                {
                    "central_sample_id": "HOOT-00001",
                    "library_source": "VIRAL_RNA",
                    "library_selection": "PCR",
                    "library_strategy": "AMPLICON",
                }
            ],
            "library_layout_config": "SINGLE",
            "library_name": library_name,
            "library_seq_kit": "KIT",
            "library_seq_protocol": "PROTOCOL",
            "username": "OAUTH",
            "token": "OAUTH"
        }

        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertIn("Failed to get or create a LibraryArtifact. Possible race condition detected", "".join(j["messages"]))
        self.assertIn("Likely caught other process in the middle of adding a LibraryArtifact, advised to resubmit", "".join(j["messages"]))

    def test_add_library_force_biosamples(self):
        library_name = "HOOT-LIB-1"
        payload = {
            "biosamples": [
                {
                    "central_sample_id": "HOOT-00001",
                    "library_source": "VIRAL_RNA",
                    "library_selection": "PCR",
                    "library_strategy": "AMPLICON",
                },
                {
                    "central_sample_id": "HOOT-00002",
                    "library_source": "VIRAL_RNA",
                    "library_selection": "PCR",
                    "library_strategy": "AMPLICON",
                }
            ],
            "library_layout_config": "SINGLE",
            "library_name": library_name,
            "library_seq_kit": "KIT",
            "library_seq_protocol": "PROTOCOL",
            "username": "OAUTH",
            "token": "OAUTH",
            "force_biosamples" : True,
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.LibraryArtifact.objects.count() == 1
        library = models.LibraryArtifact.objects.get(dice_name=library_name)
        assert library.layout_config == payload.get("library_layout_config")
        assert library.layout_read_length == payload.get("library_layout_read_length")
        assert library.layout_insert_length == payload.get("library_layout_insert_length")
        assert library.seq_kit == payload.get("library_seq_kit")
        assert library.seq_protocol == payload.get("library_seq_protocol")

        assert models.BiosampleArtifact.objects.count() == 2
        bs = models.BiosampleArtifact.objects.get(central_sample_id="HOOT-00001")
        assert bs.anonymous_sample_id == None
        bs = models.BiosampleArtifact.objects.get(central_sample_id="HOOT-00002")
        assert bs.anonymous_sample_id == None
    
    def test_add_library_force_biosample_addempty_anonymous_sample_id(self):
        library_name = "HOOT-LIB-1"
        payload = {
            "biosamples": [
                {
                    "central_sample_id": "HOOT-00001",
                    "library_source": "VIRAL_RNA",
                    "library_selection": "PCR",
                    "library_strategy": "AMPLICON",
                },
                {
                    "central_sample_id": "HOOT-00002",
                    "library_source": "VIRAL_RNA",
                    "library_selection": "PCR",
                    "library_strategy": "AMPLICON",
                }
            ],
            "library_layout_config": "SINGLE",
            "library_name": library_name,
            "library_seq_kit": "KIT",
            "library_seq_protocol": "PROTOCOL",
            "username": "OAUTH",
            "token": "OAUTH",
            "force_biosamples" : True,
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.LibraryArtifact.objects.count() == 1
        library = models.LibraryArtifact.objects.get(dice_name=library_name)
        assert library.layout_config == payload.get("library_layout_config")
        assert library.layout_read_length == payload.get("library_layout_read_length")
        assert library.layout_insert_length == payload.get("library_layout_insert_length")
        assert library.seq_kit == payload.get("library_seq_kit")
        assert library.seq_protocol == payload.get("library_seq_protocol")

        assert models.BiosampleArtifact.objects.count() == 2
        bs = models.BiosampleArtifact.objects.get(central_sample_id="HOOT-00001")
        assert bs.anonymous_sample_id == None
        bs = models.BiosampleArtifact.objects.get(central_sample_id="HOOT-00002")
        assert bs.anonymous_sample_id == None

        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        # Add empty records with id
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": "HOOT-00001", 
                    "anonymous_sample_id" : user_anonymous_sample_id,
                    "sender_sample_id" : "SECRET-00001",
                },
                {
                    "central_sample_id": "HOOT-00002", 
                    "anonymous_sample_id" : user_anonymous_sample_id_2,
                },
            ],
        }
        response = self.c.post(self.empty_bio_endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.empty_bio_token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 2
        bs = models.BiosampleArtifact.objects.get(central_sample_id="HOOT-00001")
        assert bs.anonymous_sample_id == user_anonymous_sample_id
        assert bs.sender_sample_id == "SECRET-00001"
        bs = models.BiosampleArtifact.objects.get(central_sample_id="HOOT-00002")
        assert bs.anonymous_sample_id == user_anonymous_sample_id_2
        assert bs.sender_sample_id == None
