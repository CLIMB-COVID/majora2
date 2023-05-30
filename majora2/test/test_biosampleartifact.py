import datetime
import uuid
import copy

from django.test import Client, TestCase
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from django.conf import settings

from majora2 import models
from majora2 import forms
from majora2.test.test_basic_api import BasicAPIBase, OAuthAPIClientBase

from tatl import models as tmodels

import sys
import json
import requests

default_central_sample_id = "HOOT-00001"
default_central_sample_id_2 = "HOOT-00002"

if settings.ISSUE_ZANA_IDS:
    response = requests.post(
                    "http://%s:%s/issue" % (settings.ZANA_HOST, settings.ZANA_PORT),
                    json={
                        "org_code" : settings.ZANA_POOL_ANON,
                        "prefix" : settings.ZANA_POOL_ANON,
                        "pool" : settings.ZANA_POOL_ANON,
                        "linkage_id" : default_central_sample_id,
                    }
                )
    assert response.ok
    default_anonymous_sample_id = response.json()["zeal"]
else:
    default_anonymous_sample_id = None

user_anonymous_sample_id = "%s-%s" % (settings.ANON_PREFIXES[0] if settings.ANON_PREFIXES else "TEST", "00000001")
user_anonymous_sample_id_2 = "%s-%s" % (settings.ANON_PREFIXES[0] if settings.ANON_PREFIXES else "TEST", "00000002")                     

default_payload = {
    "biosamples": [
        {
            "adm1": "UK-ENG",
            "central_sample_id": default_central_sample_id,
            "collection_date": datetime.date.today().strftime("%Y-%m-%d"),
            "is_surveillance": False,

            "received_date": datetime.date.today().strftime("%Y-%m-%d"),
            "adm2": "Birmingham",
            "source_age": 30,
            "source_sex": "M",
            "adm2_private": "B20",
            "biosample_source_id": "ABC12345",
            "collecting_org": "Hypothetical University of Hooting",
            "root_sample_id": "PHA_12345",
            "sample_type_collected": "swab",
            "sample_type_received": "primary",
            "sender_sample_id": "LAB12345",
            "swab_site": "nose-throat",

            "collection_pillar": 1,
            "is_hcw": True,
            "is_hospital_patient": True,
            "is_icu_patient": False,
            "admitted_with_covid_diagnosis": True,
            "employing_hospital_name": "Hoot Point Hospital",
            "employing_hospital_trust_or_board": "Hoot Point Hospital Trust",
            "admission_date": datetime.date.today().strftime("%Y-%m-%d"),
            "admitted_hospital_name": "Hooting Hospital",
            "admitted_hospital_trust_or_board": "Hooting Hospital Trust",
            "is_care_home_worker": False,
            "is_care_home_resident": False,
            "anonymised_care_home_code": None,

            "metadata": {
                "test": {
                    "bubo": "bubo",
                    "hoots": 8,
                    "hooting": False,

                },
                "majora": {
                    "mask": "creepy",
                }
            },
            "metrics": {
                "ct": {
                    "records": {
                        1: {
                            "test_platform": "INHOUSE",
                            "test_target": "S",
                            "test_kit": "INHOUSE",
                            "ct_value": 20,
                        },
                        2: {
                            "test_platform": "INHOUSE",
                            "test_target": "E",
                            "test_kit": "INHOUSE",
                            "ct_value": 21,
                        },
                    }
                }
            },
        },
    ],
    "client_name": "pytest",
    "client_version": 1,
}
def _test_biosample(self, bs, payload):

    # Fixed values
    self.assertEqual("United Kingdom", bs.created.collection_location_country)
    self.assertEqual("2697049", bs.taxonomy_identifier)


    self.assertEqual(payload["biosamples"][0].get("adm1"), bs.created.collection_location_adm1)
    self.assertEqual(payload["biosamples"][0]["central_sample_id"], bs.dice_name)
    self.assertEqual(default_anonymous_sample_id, bs.anonymous_sample_id)
    self.assertEqual(datetime.datetime.strptime(payload["biosamples"][0]["collection_date"], "%Y-%m-%d").date(), bs.created.collection_date)

    if hasattr(bs.created, "coguk_supp"):
        self.assertEqual(payload["biosamples"][0].get("is_surveillance"), bs.created.coguk_supp.is_surveillance)
        self.assertEqual(payload["biosamples"][0].get("collection_pillar"), bs.created.coguk_supp.collection_pillar)
        self.assertEqual(payload["biosamples"][0].get("is_hcw"), bs.created.coguk_supp.is_hcw)
        self.assertEqual(payload["biosamples"][0].get("is_hospital_patient"), bs.created.coguk_supp.is_hospital_patient)
        self.assertEqual(payload["biosamples"][0].get("is_icu_patient"), bs.created.coguk_supp.is_icu_patient)
        self.assertEqual(payload["biosamples"][0].get("admitted_with_covid_diagnosis"), bs.created.coguk_supp.admitted_with_covid_diagnosis)
        self.assertEqual(payload["biosamples"][0].get("employing_hospital_name"), bs.created.coguk_supp.employing_hospital_name)
        self.assertEqual(payload["biosamples"][0].get("employing_hospital_trust_or_board"), bs.created.coguk_supp.employing_hospital_trust_or_board)

        admission_date = None
        try:
            admission_date = datetime.datetime.strptime(payload["biosamples"][0].get("admission_date"), "%Y-%m-%d").date()
        except TypeError:
            pass
        self.assertEqual(admission_date, bs.created.coguk_supp.admission_date)

        self.assertEqual(payload["biosamples"][0].get("admitted_hospital_name"), bs.created.coguk_supp.admitted_hospital_name)
        self.assertEqual(payload["biosamples"][0].get("admitted_hospital_trust_or_board"), bs.created.coguk_supp.admitted_hospital_trust_or_board)
        self.assertEqual(payload["biosamples"][0].get("is_care_home_worker"), bs.created.coguk_supp.is_care_home_worker)
        self.assertEqual(payload["biosamples"][0].get("is_care_home_resident"), bs.created.coguk_supp.is_care_home_resident)
        self.assertEqual(payload["biosamples"][0].get("anonymised_care_home_code"), bs.created.coguk_supp.anonymised_care_home_code)

    received_date = None
    try:
        received_date = datetime.datetime.strptime(payload["biosamples"][0].get("received_date"), "%Y-%m-%d").date()
    except TypeError:
        pass
    self.assertEqual(received_date, bs.created.received_date)

    adm2 = None
    try:
        adm2 = payload["biosamples"][0].get("adm2").upper() #adm2 coerced to upper
    except AttributeError:
        pass
    self.assertEqual(adm2, bs.created.collection_location_adm2)
    self.assertEqual(payload["biosamples"][0].get("source_age"), bs.created.source_age)
    self.assertEqual(payload["biosamples"][0].get("source_sex", ""), bs.created.source_sex)
    self.assertEqual(payload["biosamples"][0].get("adm2_private"), bs.created.private_collection_location_adm2)

    biosample_sources = []
    for record in bs.created.records.all():
        if record.in_group and record.in_group.kind == "Biosample Source":
            biosample_sources.append(record.in_group.secondary_id)

    if payload["biosamples"][0].get("biosample_source_id"):
        self.assertEqual(payload["biosamples"][0]["biosample_source_id"], biosample_sources[0])
        self.assertEqual(payload["biosamples"][0]["biosample_source_id"], bs.primary_group.dice_name)
        self.assertEqual(len(biosample_sources), 1)
    else:
        self.assertEqual(len(biosample_sources), 0)
        self.assertEqual(None, bs.primary_group)

    self.assertEqual(payload["biosamples"][0].get("collecting_org"), bs.created.collected_by)
    self.assertEqual(self.user, bs.created.submission_user)
    self.assertEqual(self.user.profile.institute.name, bs.created.submitted_by)
    self.assertEqual(self.user.profile.institute, bs.created.submission_org)

    self.assertEqual(payload["biosamples"][0].get("root_sample_id"), bs.root_sample_id)
    self.assertEqual(payload["biosamples"][0].get("sample_type_collected", ""), bs.sample_type_collected)
    self.assertEqual(payload["biosamples"][0].get("sample_type_received"), bs.sample_type_current)
    self.assertEqual(payload["biosamples"][0].get("sender_sample_id"), bs.sender_sample_id)
    self.assertEqual(payload["biosamples"][0].get("swab_site"), bs.sample_site)

    # Metadata
    expected_n_metadata = 0
    for tag_name, tag_data in payload["biosamples"][0]["metadata"].items():
        expected_n_metadata += len(tag_data.keys())

    self.assertEqual(bs.metadata.count(), expected_n_metadata)
    record_tests = 0
    for record in bs.metadata.all():
        self.assertEqual(str(payload["biosamples"][0]["metadata"][record.meta_tag][record.meta_name]), record.value) # all metadata is str atm
        record_tests += 1
    self.assertEqual(record_tests, expected_n_metadata)

    # Metrics
    expected_n_metrics_objects = 0
    expected_n_metrics_records = 0
    for tag_name, tag_data in payload["biosamples"][0]["metrics"].items():
        expected_n_metrics_objects += 1
        expected_n_metrics_records += len(tag_data["records"])

    n_records = 0
    self.assertEqual(bs.metrics.count(), expected_n_metrics_objects)
    for metric in bs.metrics.all():
        for record in metric.metric_records.all():
            n_records += 1
    self.assertEqual(n_records, expected_n_metrics_records)

    record_tests = 0
    if expected_n_metrics_objects > 0:
        for i, metric in payload["biosamples"][0]["metrics"]["ct"]["records"].items():
            self.assertIsNotNone(models.TemporaryMajoraArtifactMetricRecord_ThresholdCycle.objects.filter(
                artifact_metric__artifact=bs,
                test_platform = metric["test_platform"],
                test_kit = metric["test_kit"],
                test_target = metric["test_target"],
                ct_value = metric["ct_value"]
            ).first())
            record_tests += 1
    self.assertEqual(record_tests, expected_n_metrics_records)

class BiosampleArtifactTest(BasicAPIBase):
    def setUp(self):
        super().setUp()
        self.default_central_sample_id = default_central_sample_id
        self.default_payload = copy.deepcopy(default_payload)
        self.default_payload["username"] = self.user.username
        self.default_payload["token"] = self.key.key

    def _add_biosample(self, payload, expected_errors=0, update=False, empty=False, expected_http=200):
        endpoint = "api.artifact.biosample.add"
        if update:
            endpoint = "api.artifact.biosample.update"
        elif empty:
            endpoint = "api.artifact.biosample.addempty"

        response = self.c.post(reverse(endpoint), payload, secure=True, content_type="application/json")
        self.assertEqual(expected_http, response.status_code)

        j = None
        if expected_http == 200:
            j = response.json()
            if j["errors"] != expected_errors:
                sys.stderr.write(json.dumps(j, indent=4, sort_keys=True) + '\n')
            self.assertEqual(expected_errors, j["errors"])

        bs = None
        try:
            bs = models.BiosampleArtifact.objects.get(central_sample_id=self.default_central_sample_id)
        except models.BiosampleArtifact.DoesNotExist:
            pass
        return bs, j

    def test_add_biosample(self):
        payload = copy.deepcopy(self.default_payload)

        n_biosamples = models.BiosampleArtifact.objects.count()
        bs, j = self._add_biosample(payload)
        self.assertEqual(models.BiosampleArtifact.objects.count(), n_biosamples+1)

        _test_biosample(self, bs, payload)


    def test_biosample_pha_update(self):
        # create a biosample
        payload = copy.deepcopy(self.default_payload)
        self._add_biosample(payload)

        update_payload = {
            "username": self.user.username,
            "token": self.key.key,
            "biosamples": [
                {
                    "central_sample_id": "HOOT-00001",
                    "root_biosample_source_id": "HOOTER-1",
                },
            ],
            "client_name": "pytest",
            "client_version": 1,
        }
        self._add_biosample(update_payload, update=True)

        bs = models.BiosampleArtifact.objects.get(central_sample_id=self.default_central_sample_id)
        self.assertEqual(update_payload["biosamples"][0]["root_biosample_source_id"], bs.root_biosample_source_id)
        _test_biosample(self, bs, payload) # determine nothing has changed from the initial payload

    def test_biosample_update(self):
        # create a biosample
        payload = copy.deepcopy(self.default_payload)
        self._add_biosample(payload)

        update_payload = {
            "username": self.user.username,
            "token": self.key.key,
            "biosamples": [
                {
                    "adm1": "UK-WLS",
                    "central_sample_id": self.default_central_sample_id,
                    "collection_date": datetime.date.today().strftime("%Y-%m-%d"),
                    "is_surveillance": True,

                    "received_date": datetime.date.today().strftime("%Y-%m-%d"),
                    "adm2": "Swansea",
                    "source_age": 31,
                    "source_sex": "F",
                    "adm2_private": "SA4",
                    "biosample_source_id": "XYZ12345",
                    "collecting_org": "Parliament of Hooters",
                    "root_sample_id": "PHA_67890",
                    "sample_type_collected": "BAL",
                    "sample_type_received": "primary",
                    "sender_sample_id": "LAB67890",
                    "swab_site": None,

                    "collection_pillar": 2,
                    "is_hcw": False,
                    "is_hospital_patient": True,
                    "is_icu_patient": True,
                    "admitted_with_covid_diagnosis": False,
                    "employing_hospital_name": None,
                    "employing_hospital_trust_or_board": None,
                    "admission_date": datetime.date.today().strftime("%Y-%m-%d"),
                    "admitted_hospital_name": "HOSPITAL",
                    "admitted_hospital_trust_or_board": "HOSPITAL",
                    "is_care_home_worker": True,
                    "is_care_home_resident": True,
                    "anonymised_care_home_code": "CC-X00",

                    "metadata": {
                        "test": {
                            "bubo": "bubo",
                            "hoots": 8,
                            "hooting": False,

                        },
                        "majora": {
                            "mask": "creepy",
                        }
                    },
                    "metrics": {
                        "ct": {
                            "records": {
                                1: {
                                    "test_platform": "INHOUSE",
                                    "test_target": "S",
                                    "test_kit": "INHOUSE",
                                    "ct_value": 20,
                                },
                                2: {
                                    "test_platform": "INHOUSE",
                                    "test_target": "E",
                                    "test_kit": "INHOUSE",
                                    "ct_value": 21,
                                },
                            }
                        }
                    },
                },
            ],
            "client_name": "pytest",
            "client_version": 1,
        }
        bs, j = self._add_biosample(update_payload)

        with self.assertRaises(AssertionError):
            # Check that the biosample has changed from the initial
            _test_biosample(self, bs, payload)
        _test_biosample(self, bs, update_payload)

        # Check the supp has been updated and not recreated
        self.assertEqual(models.COGUK_BiosourceSamplingProcessSupplement.objects.count(), 1)

    def test_biosample_add_overwrite_metadata(self):
        # create a biosample
        payload = copy.deepcopy(self.default_payload)
        bs, j = self._add_biosample(payload)

        update_payload = copy.deepcopy(self.default_payload)
        update_payload["biosamples"][0]["metadata"]["test"]["hooting"] = True
        update_payload["biosamples"][0]["metadata"]["majora"]["mask"] = "cute"
        update_payload["biosamples"][0]["metrics"] = {}
        bs, j = self._add_biosample(update_payload)

        with self.assertRaises(AssertionError):
            # Check that the biosample has changed from the initial
            _test_biosample(self, bs, payload)

        update_payload["biosamples"][0]["metrics"] = payload["biosamples"][0]["metrics"] # reinsert to check metrics have stayed
        _test_biosample(self, bs, update_payload)

        # Check tatl
        expected_context = {
            "changed_fields": [],
            "nulled_fields": [],
            "changed_metadata": ["metadata:test.hooting", "metadata:majora.mask"],
            "flashed_metrics": [],
        }
        self._test_update_biosample_tatl(j["request"], expected_context)

    def test_biosample_add_overwrite_metrics(self):
        # create a biosample
        payload = copy.deepcopy(self.default_payload)
        bs, j = self._add_biosample(payload)

        update_payload = copy.deepcopy(self.default_payload)
        update_payload["biosamples"][0]["metrics"]["ct"]["records"][2]["ct_value"] = 30
        bs, j = self._add_biosample(update_payload)

        with self.assertRaises(AssertionError):
            # Check that the biosample has changed from the initial
            _test_biosample(self, bs, payload)
        _test_biosample(self, bs, update_payload)

        # Check tatl
        expected_context = {
            "changed_fields": [],
            "nulled_fields": [],
            "changed_metadata": [],
            "flashed_metrics": ["ct"],
        }
        self._test_update_biosample_tatl(j["request"], expected_context)

    def test_biosample_add_update_nostomp(self):
        # create a biosample
        payload = copy.deepcopy(self.default_payload)
        bs, j = self._add_biosample(payload)

        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["collection_pillar"] = 2

        bs, j = self._add_biosample(payload)
        _test_biosample(self, bs, payload) # compare object to payload

    def test_biosample_add_update_nuke_stomp(self):
        #NOTE Some fields become "" empty string when sending None
        #TODO   it would be nice if that behaviour was consistent

        # create a biosample
        payload = copy.deepcopy(self.default_payload)
        bs, j = self._add_biosample(payload)

        stomp_payload = {
            "username": self.user.username,
            "token": self.key.key,
            "biosamples": [
                {
                    "adm1": "UK-ENG",
                    "central_sample_id": self.default_central_sample_id,
                    "collection_date": datetime.date.today().strftime("%Y-%m-%d"),
                    "is_surveillance": False,

                    "received_date": None,
                    "adm2": None,
                    "source_age": None,
                    "source_sex": "",
                    "adm2_private": None,
                    "biosample_source_id": "ABC12345", # can't nuke biosample_source_id once it has been set
                    "collecting_org": None,
                    "root_sample_id": None,
                    "sample_type_collected": "",
                    "sample_type_received": None,
                    "sender_sample_id": None,
                    "swab_site": None,

                    "collection_pillar": None,
                    "is_hcw": None,
                    "is_hospital_patient": None,
                    "is_icu_patient": None,
                    "admitted_with_covid_diagnosis": None,
                    "employing_hospital_name": None,
                    "employing_hospital_trust_or_board": None,
                    "admission_date": None,
                    "admitted_hospital_name": None,
                    "admitted_hospital_trust_or_board": None,
                    "is_care_home_worker": None,
                    "is_care_home_resident": None,
                    "anonymised_care_home_code": None,
                    "metadata": {},
                    "metrics": {},
                },
            ],
            "client_name": "pytest",
            "client_version": 1,
        }
        bs, j = self._add_biosample(stomp_payload)

        # Add the metadata and metrics back to show that blanking them does nothing
        stomp_payload["biosamples"][0]["metadata"] = payload["biosamples"][0]["metadata"]
        stomp_payload["biosamples"][0]["metrics"] = payload["biosamples"][0]["metrics"]
        _test_biosample(self, bs, stomp_payload) # compare object to payload

        # Check the supp has been updated and not recreated
        self.assertEqual(models.COGUK_BiosourceSamplingProcessSupplement.objects.count(), 1)


    def test_biosample_minimal_add_metrics_update(self):
        # Add a minimal biosample and update it with some metrics
        payload = {
            "username": self.user.username,
            "token": self.key.key,
            "biosamples": [
                {
                    "adm1": "UK-ENG",
                    "central_sample_id": self.default_central_sample_id,
                    "collection_date": datetime.date.today().strftime("%Y-%m-%d"),
                    "is_surveillance": False,
                    "is_hcw": True,
                    "metadata": {},
                    "metrics": {},
                },
            ],
            "client_name": "pytest",
            "client_version": 1,
        }
        bs, j = self._add_biosample(payload)
        _test_biosample(self, bs, payload)

        new_payload = {
            "username": self.user.username,
            "token": self.key.key,
            "biosamples": [
                {
                    "central_sample_id": self.default_central_sample_id,
                    "metadata": {
                        "test": {
                            "bubo": "bubo",
                            "hoots": 8,
                            "hooting": False,

                        },
                        "majora": {
                            "mask": "creepy",
                        }
                    },
                    "metrics": {
                        "ct": {
                            "records": {
                                1: {
                                    "test_platform": "INHOUSE",
                                    "test_target": "S",
                                    "test_kit": "INHOUSE",
                                    "ct_value": 20,
                                },
                                2: {
                                    "test_platform": "INHOUSE",
                                    "test_target": "E",
                                    "test_kit": "INHOUSE",
                                    "ct_value": 21,
                                },
                            }
                        }
                    },
                },
            ],
        }
        bs, j = self._add_biosample(new_payload, update=True)

        update_payload = copy.deepcopy(payload)
        update_payload["biosamples"][0]["metadata"] = new_payload["biosamples"][0]["metadata"]
        update_payload["biosamples"][0]["metrics"] = new_payload["biosamples"][0]["metrics"]
        _test_biosample(self, bs, update_payload)

    def test_biosample_full_add_partial_update(self):
        # Add a full biosample and update a few additional fields that were placeholded
        payload = copy.deepcopy(self.default_payload)
        bs, j = self._add_biosample(payload)
        _test_biosample(self, bs, payload)

        payload["biosamples"][0]["is_surveillance"] = True
        payload["biosamples"][0]["collection_pillar"] = 2
        bs, j = self._add_biosample(payload, update=True)
        _test_biosample(self, bs, payload)

    def test_biosample_minimal_add_partial_update(self):
        # Add a minimal biosample and update a few additional fields
        payload = {
            "username": self.user.username,
            "token": self.key.key,
            "biosamples": [
                {
                    "adm1": "UK-ENG",
                    "central_sample_id": self.default_central_sample_id,
                    "collection_date": datetime.date.today().strftime("%Y-%m-%d"),
                    "is_surveillance": False,
                    "is_hcw": True,
                    "metadata": {},
                    "metrics": {},
                },
            ],
            "client_name": "pytest",
            "client_version": 1,
        }
        bs, j = self._add_biosample(payload)
        _test_biosample(self, bs, payload)

        new_payload = copy.deepcopy(payload)
        del new_payload["biosamples"][0]["adm1"]
        del new_payload["biosamples"][0]["collection_date"]

        new_payload["biosamples"][0]["is_surveillance"] = True
        payload["biosamples"][0]["is_surveillance"] = True

        new_payload["biosamples"][0]["collection_pillar"] = 2
        payload["biosamples"][0]["collection_pillar"] = 2

        with self.assertRaises(AssertionError):
            # Check that the biosample has changed from the last
            _test_biosample(self, bs, payload)

        bs, j = self._add_biosample(new_payload, update=True)
        _test_biosample(self, bs, payload)


    def test_biosample_full_add_single_update(self):
        # create a biosample
        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["metrics"] = {} # ignore metrics
        bs, j = self._add_biosample(payload)

        del payload["biosamples"][0]["is_hcw"]
        del payload["biosamples"][0]["is_hospital_patient"]
        del payload["biosamples"][0]["is_icu_patient"]
        del payload["biosamples"][0]["admitted_with_covid_diagnosis"]
        del payload["biosamples"][0]["employing_hospital_name"]
        del payload["biosamples"][0]["employing_hospital_trust_or_board"]
        del payload["biosamples"][0]["admission_date"]
        del payload["biosamples"][0]["admitted_hospital_name"]
        del payload["biosamples"][0]["admitted_hospital_trust_or_board"]
        del payload["biosamples"][0]["is_care_home_worker"]
        del payload["biosamples"][0]["is_care_home_resident"]
        del payload["biosamples"][0]["anonymised_care_home_code"]

        del payload["biosamples"][0]["collection_date"]
        del payload["biosamples"][0]["received_date"]
        del payload["biosamples"][0]["source_age"]
        del payload["biosamples"][0]["source_sex"]
        del payload["biosamples"][0]["adm1"]
        del payload["biosamples"][0]["adm2"]
        del payload["biosamples"][0]["adm2_private"]
        del payload["biosamples"][0]["collecting_org"]

        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        partial_fields = {
            "collection_date": yesterday,
            "received_date": yesterday,
            "source_age": 29,
            "source_sex": "F",
            "adm1": "UK-WLS",
            "adm2": "SWANSEA",
            "adm2_private": "SA4",
            "collecting_org": "Hooting High Hospital",

            "is_hcw": False,
            "is_hospital_patient": False,
            "is_icu_patient": True,
            "admitted_with_covid_diagnosis": False,
            "employing_hospital_name": "HOSPITAL",
            "employing_hospital_trust_or_board": "HOSPITAL",
            "admission_date": None,
            "admitted_hospital_name": "HOSPITAL",
            "admitted_hospital_trust_or_board": "HOSPITAL",
            "is_care_home_worker": True,
            "is_care_home_resident": True,
            "anonymised_care_home_code": "CC-X00",
        }
        check_payload = copy.deepcopy(self.default_payload)
        check_payload["biosamples"][0]["metrics"] = {} # ignore metrics
        for k, v in partial_fields.items():
            update_payload = copy.deepcopy(payload)
            update_payload["biosamples"][0][k] = v

            bs, j = self._add_biosample(update_payload, update=True)

            with self.assertRaises(AssertionError):
                # Check that the biosample has changed from the last
                _test_biosample(self, bs, check_payload)

            check_payload["biosamples"][0][k] = v
            _test_biosample(self, bs, check_payload) # compare object to payload

            # Check tatl
            expected_context = {
                "changed_fields": [],
                "nulled_fields": [],
                "changed_metadata": [],
                "flashed_metrics": [],
            }
            if v is None:
                expected_context["nulled_fields"].append(k)
            else:
                expected_context["changed_fields"].append(k)
            self._test_update_biosample_tatl(j["request"], expected_context)


    def test_reject_partial_new_biosampleartifact(self):
        payload = {
            "username": self.user.username,
            "token": self.key.key,
            "biosamples": [
                {
                    "adm1": "UK-ENG",
                    "central_sample_id": self.default_central_sample_id,
                    "collection_date": datetime.date.today().strftime("%Y-%m-%d"),
                    "is_surveillance": False,
                    "is_hcw": True,
                    "metadata": {},
                    "metrics": {},
                },
            ],
            "client_name": "pytest",
            "client_version": 1,
        }
        bs, j = self._add_biosample(payload, expected_errors=1, update=True)
        self.assertIsNone(bs)
        self.assertIn("Cannot use `partial` on new BiosampleArtifact %s" % self.default_central_sample_id, j["messages"])


    def test_add_biosample_tatl(self):
        payload = copy.deepcopy(self.default_payload)
        bs, j = self._add_biosample(payload)

        tatl = tmodels.TatlRequest.objects.filter(response_uuid=j["request"]).first()
        self.assertIsNotNone(tatl)

        self.assertEqual(tatl.verbs.count(), 2)

        expected_verbs = [
            ("CREATE", models.BiosampleArtifact.objects.get(dice_name=self.default_central_sample_id)),
            ("CREATE", models.BiosampleSource.objects.get(dice_name="ABC12345")),
        ]

        for verb in tatl.verbs.all():
            self.assertIn( (verb.verb, verb.content_object), expected_verbs )

    def _test_update_biosample_tatl(self, request_id, expected_context):
        tatl = tmodels.TatlRequest.objects.filter(response_uuid=request_id).first()
        self.assertIsNotNone(tatl)

        self.assertEqual(tatl.verbs.count(), 1)

        expected_verbs = [
            ("UPDATE", models.BiosampleArtifact.objects.get(dice_name=self.default_central_sample_id)),
        ]
        verb = tatl.verbs.all()[0]
        extra_j = json.loads(verb.extra_context)

        self.assertIn("changed_fields", extra_j)
        self.assertIn("nulled_fields", extra_j)
        self.assertIn("changed_metadata", extra_j)
        self.assertIn("flashed_metrics", extra_j)

        self.assertEqual(len(extra_j["changed_fields"]), len(expected_context["changed_fields"]))
        self.assertEqual(len(extra_j["nulled_fields"]), len(expected_context["nulled_fields"]))
        self.assertEqual(len(extra_j["changed_metadata"]), len(expected_context["changed_metadata"]))
        self.assertEqual(len(extra_j["flashed_metrics"]), len(expected_context["flashed_metrics"]))

        # Use modelform classmethod to resolve the correct mapping
        # Cheat and convert the list to a dict so it works as a payload
        for cat in expected_context:
            d = {}
            for k in expected_context[cat]:
                d[k] = None

            d = forms.BiosampleArtifactModelForm.map_request_fields(d)
            d = forms.BiosourceSamplingProcessModelForm.map_request_fields(d) # pass through each form used by the interface

            for f in d:
                self.assertIn(f, extra_j[cat])


    def test_empty_biosample_noscope(self):
        payload = {
            "biosamples": [
                self.default_central_sample_id,
            ]
        }
        # By default users do not have scope to force samples
        self._add_biosample(payload, empty=True, expected_http=400)

    def test_empty_biosample_okscope_nooauth(self):
        fp = Permission.objects.get(codename="force_add_biosampleartifact")
        self.user.user_permissions.add(fp)
        self.user.save()
        payload = {
            "username": self.user.username,
            "token": self.key.key,
            "biosamples": [
                self.default_central_sample_id,
            ],
            "client_name": "pytest",
            "client_version": 1,
        }
        self._add_biosample(payload, empty=True, expected_http=400)
        self.user.user_permissions.remove(fp) # urgh better hope we dont run parallel tests eh
        self.user.save()

    # Test nuke metadata (with new None)
    # Test nuke ct (currently only nuked on new)
    # Test mod preform
    # Test initial data is stompy

class OAuthBiosampleArtifactTest(OAuthAPIClientBase):
    def setUp(self):
        super().setUp()

        self.endpoint = reverse("api.artifact.biosample.add")

        self.scope = "majora2.add_biosampleartifact majora2.change_biosampleartifact majora2.add_biosamplesource majora2.change_biosamplesource majora2.add_biosourcesamplingprocess majora2.change_biosourcesamplingprocess"
        self.token = self._get_token(self.scope)

        self.update_endpoint = reverse("api.artifact.biosample.update")
        self.update_scope = "majora2.change_biosampleartifact majora2.add_biosamplesource majora2.change_biosamplesource majora2.change_biosourcesamplingprocess"
        self.update_token = self._get_token(self.scope)

        self.default_central_sample_id = default_central_sample_id
        self.default_payload = copy.deepcopy(default_payload)
        self.default_payload["username"] = "user"
        self.default_payload["token"] = "oauth"

    def test_add_biosample_ok(self):
        n_biosamples = models.BiosampleArtifact.objects.count()

        payload = copy.deepcopy(self.default_payload)
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        self.assertEqual(models.BiosampleArtifact.objects.count(), n_biosamples+1)

        assert models.BiosampleArtifact.objects.filter(central_sample_id=self.default_central_sample_id).count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=self.default_central_sample_id)
        _test_biosample(self, bs, payload)

        # Check the validity endpoint
        payload = {
            "username": "hoot",
            "token": "oauth",
            "biosamples": [
                self.default_central_sample_id,
            ],
        }
        response = self.c.post(reverse("api.artifact.biosample.query.validity"), payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()

        assert j["result"][self.default_central_sample_id]["exists"] == True
        assert j["result"][self.default_central_sample_id]["has_sender_id"] == True
        assert j["result"][self.default_central_sample_id]["has_metadata"] == True

    def test_add_biosample_bad_scope_bad(self):
        n_biosamples = models.BiosampleArtifact.objects.count()

        payload = copy.deepcopy(self.default_payload)
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.tokens["bad_scope"])
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertIn("Your token is valid but does not have all of the scopes to perform this action.", "".join(j["messages"]))

    def test_add_biosample_oldsampledate_bad(self):
        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["collection_date"] = (datetime.datetime.now() - datetime.timedelta(days=366)).strftime("%Y-%m-%d")
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertIn("Sample cannot be collected more than a year ago", "".join(j["messages"][0]["collection_date"][0]["message"]))

        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["received_date"] = (datetime.datetime.now() - datetime.timedelta(days=366)).strftime("%Y-%m-%d")
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertIn("Sample cannot be received more than a year ago", "".join(j["messages"][0]["received_date"][0]["message"]))

    def test_add_biosample_receivedbeforecollection_bad(self):
        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["collection_date"] = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        payload["biosamples"][0]["received_date"] = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertIn("Sample cannot be collected after it was received", "".join(j["messages"][0]["collection_date"][0]["message"]))

    def test_add_biosample_oldsampledate_update_ok(self):
        payload = copy.deepcopy(self.default_payload)
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        assert models.BiosampleArtifact.objects.filter(central_sample_id=self.default_central_sample_id).count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=self.default_central_sample_id)

        # Force the sample to be old
        old_date = (datetime.datetime.now() - datetime.timedelta(days=366))
        bs.created.collection_date = old_date
        bs.created.save()

        # Update the biosample
        payload["biosamples"][0]["collection_date"] = old_date.strftime("%Y-%m-%d")
        payload["biosamples"][0]["adm2"] = "Hootington"
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        j = response.json()
        self.assertEqual(j["errors"], 0)

        assert models.BiosampleArtifact.objects.filter(central_sample_id=self.default_central_sample_id).count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=self.default_central_sample_id)
        _test_biosample(self, bs, payload)

    def test_add_biosample_pastsampledate_nearlybad(self):
        payload = copy.deepcopy(self.default_payload)
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        assert models.BiosampleArtifact.objects.filter(central_sample_id=self.default_central_sample_id).count() == 1

        payload["biosamples"][0]["collection_date"] = "2019-12-31"
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertIn("Sample cannot be collected before 2020", "".join(j["messages"][0]["collection_date"][0]["message"]))

        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["received_date"] = "2019-12-31"
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertIn("Sample cannot be received before 2020", "".join(j["messages"][0]["received_date"][0]["message"]))

    def test_add_biosample_pastsampledate_verybad(self):
        payload = copy.deepcopy(self.default_payload)
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        assert models.BiosampleArtifact.objects.filter(central_sample_id=self.default_central_sample_id).count() == 1

        payload["biosamples"][0]["collection_date"] = "1899-12-30"
        payload["biosamples"][0]["received_date"] = None
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertIn("Sample cannot be collected before 2020", "".join(j["messages"][0]["collection_date"][0]["message"]))

        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["collection_date"] = None
        payload["biosamples"][0]["received_date"] = "1899-12-30"
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertIn("Sample cannot be received before 2020", "".join(j["messages"][0]["received_date"][0]["message"]))

    def test_add_biosample_pastsampledate_notbad(self):
        payload = copy.deepcopy(self.default_payload)
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        assert models.BiosampleArtifact.objects.filter(central_sample_id=self.default_central_sample_id).count() == 1

        payload["biosamples"][0]["collection_date"] = "2020-01-01"
        payload["biosamples"][0]["received_date"] = None
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        bs = models.BiosampleArtifact.objects.get(central_sample_id=self.default_central_sample_id)
        assert bs.created.collection_date == datetime.datetime.strptime("2020-01-01", "%Y-%m-%d").date()

        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["collection_date"] = None
        payload["biosamples"][0]["received_date"] = "2020-01-01"
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        bs = models.BiosampleArtifact.objects.get(central_sample_id=self.default_central_sample_id)
        assert bs.created.received_date == datetime.datetime.strptime("2020-01-01", "%Y-%m-%d").date()

    def test_add_biosample_futuresampledate_bad(self):
        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["collection_date"] = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        payload["biosamples"][0]["received_date"] = None
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertIn("Sample cannot be collected in the future", "".join(j["messages"][0]["collection_date"][0]["message"]))

        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["collection_date"] = None
        payload["biosamples"][0]["received_date"] = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertIn("Sample cannot be received in the future", "".join(j["messages"][0]["received_date"][0]["message"]))
    
    def test_add_biosample_anonymous_sample_id_default_ok(self):
        payload = copy.deepcopy(self.default_payload)
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == default_anonymous_sample_id

    def test_add_biosample_anonymous_sample_id_null_default_ok(self):
        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["anonymous_sample_id"] = ""
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == default_anonymous_sample_id

    def test_add_biosample_anonymous_sample_id_ok(self):
        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["anonymous_sample_id"] = user_anonymous_sample_id
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

    def test_change_biosample_anonymous_sample_id_null_reset_ok(self):
        payload = copy.deepcopy(self.default_payload)
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == default_anonymous_sample_id
        
        # Something terrible has happened
        bs.anonymous_sample_id = None
        bs.save()

        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == None

        # Empty update, should set id back to normal
        update_payload = {
            "username": "user",
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id,
                }

            ],
            "client_name": "pytest",
            "client_version": 1,
        }
        response = self.c.post(self.update_endpoint, update_payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.update_token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == default_anonymous_sample_id 

    def test_change_biosample_anonymous_sample_id_ok(self):
        payload = copy.deepcopy(self.default_payload)
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == default_anonymous_sample_id

        perm = Permission.objects.get(codename="can_change_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        # Change id on add
        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["anonymous_sample_id"] = user_anonymous_sample_id
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

        # Change id on update
        update_payload = {
            "username": "user",
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id,
                    "anonymous_sample_id" : user_anonymous_sample_id_2,
                }

            ],
            "client_name": "pytest",
            "client_version": 1,
        }
        response = self.c.post(self.update_endpoint, update_payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.update_token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id_2
    
    def test_add_change_biosample_anonymous_sample_id_preserved_ok(self):
        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        # Add, with id
        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["anonymous_sample_id"] = user_anonymous_sample_id
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

        # Add, without id
        payload = copy.deepcopy(self.default_payload)
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id  

        # Partial update changing nothing
        update_payload = {
            "username": "user",
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id,
                }

            ],
            "client_name": "pytest",
            "client_version": 1,
        }
        response = self.c.post(self.update_endpoint, update_payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.update_token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id
    
    def test_add_change_biosample_anonymous_sample_id_null_preserved_ok(self):
        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        # Add, with id
        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["anonymous_sample_id"] = user_anonymous_sample_id
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

        # Add, with id key but its empty
        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["anonymous_sample_id"] = ""
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id  

        # Partial update, with id key but its empty
        update_payload = {
            "username": "user",
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id,
                    "anonymous_sample_id" : "",
                }

            ],
            "client_name": "pytest",
            "client_version": 1,
        }
        response = self.c.post(self.update_endpoint, update_payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.update_token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

    def test_add_biosample_anonymous_sample_id_duplicate_bad(self):
        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["anonymous_sample_id"] = user_anonymous_sample_id
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["central_sample_id"] = default_central_sample_id_2
        payload["biosamples"][0]["anonymous_sample_id"] = user_anonymous_sample_id
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertEqual("Biosample artifact with this Anonymous sample id already exists.", "".join(j["messages"][0]["anonymous_sample_id"][0]["message"]))
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

    def test_change_biosample_anonymous_sample_id_duplicate_bad(self):
        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["anonymous_sample_id"] = user_anonymous_sample_id
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["central_sample_id"] = default_central_sample_id_2
        payload["biosamples"][0]["anonymous_sample_id"] = user_anonymous_sample_id_2
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 2
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id_2)
        assert bs.anonymous_sample_id == user_anonymous_sample_id_2

        perm = Permission.objects.get(codename="can_change_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        # Change id on update
        update_payload = {
            "username": "user",
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id_2,
                    "anonymous_sample_id" : user_anonymous_sample_id,
                }

            ],
            "client_name": "pytest",
            "client_version": 1,
        }
        response = self.c.post(self.update_endpoint, update_payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.update_token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertEqual("Biosample artifact with this Anonymous sample id already exists.", "".join(j["messages"][0]["anonymous_sample_id"][0]["message"]))
        assert models.BiosampleArtifact.objects.filter().count() == 2
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id_2)
        assert bs.anonymous_sample_id == user_anonymous_sample_id_2

    def test_add_biosample_anonymous_sample_id_noperm_bad(self):
        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["anonymous_sample_id"] = user_anonymous_sample_id
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertEqual("You do not have permission to add the anonymous_sample_id on BiosampleArtifact %s" % default_central_sample_id, "".join(j["messages"][0]))
        assert models.BiosampleArtifact.objects.count() == 0
    
    def test_change_biosample_anonymous_sample_id_noperm_bad(self):
        payload = copy.deepcopy(self.default_payload)
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == default_anonymous_sample_id

        # ID is the same, no effect on add
        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["anonymous_sample_id"] = default_anonymous_sample_id
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == default_anonymous_sample_id

        # ID is the same, no effect on update
        update_payload = {
            "username": "user",
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id,
                    "anonymous_sample_id" : default_anonymous_sample_id,
                }

            ],
            "client_name": "pytest",
            "client_version": 1,
        }
        response = self.c.post(self.update_endpoint, update_payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.update_token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == default_anonymous_sample_id

        # ID is different, rejected on add
        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["anonymous_sample_id"] = user_anonymous_sample_id
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertEqual("You do not have permission to change the anonymous_sample_id on BiosampleArtifact %s" % default_central_sample_id, "".join(j["messages"][0]))
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == default_anonymous_sample_id

        # ID is different, rejected on update
        update_payload = {
            "username": "user",
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id,
                    "anonymous_sample_id" : user_anonymous_sample_id,
                }

            ],
            "client_name": "pytest",
            "client_version": 1,
        }
        response = self.c.post(self.update_endpoint, update_payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.update_token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertEqual("You do not have permission to change the anonymous_sample_id on BiosampleArtifact %s" % default_central_sample_id, "".join(j["messages"][0]))
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == default_anonymous_sample_id

    def test_add_biosample_anonymous_sample_id_wrongformat_bad(self):
        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["anonymous_sample_id"] = "%s-%s" % (settings.ANON_PREFIXES[0] if settings.ANON_PREFIXES else "TEST", "000-0001") 
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertEqual("anonymous_sample_id must consist of a prefix and postfix, separated by a single '-' character", "".join(j["messages"][0]["anonymous_sample_id"][0]["message"]))
        assert models.BiosampleArtifact.objects.count() == 0

    def test_add_biosample_anonymous_sample_id_wrongprefix_bad(self):
        if settings.ANON_PREFIXES:
            badprefix = "".join(settings.ANON_PREFIXES) * 2
            perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
            self.user.user_permissions.add(perm)

            payload = copy.deepcopy(self.default_payload)
            payload["biosamples"][0]["anonymous_sample_id"] = "%s-%s" % (badprefix, "00000001") 
            response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
            self.assertEqual(200, response.status_code)
            j = response.json()
            self.assertEqual(j["errors"], 1)
            self.assertEqual("anonymous_sample_id has an invalid prefix: %s" % badprefix, "".join(j["messages"][0]["anonymous_sample_id"][0]["message"]))
            assert models.BiosampleArtifact.objects.count() == 0

    def test_add_biosample_anonymous_sample_id_wrongpostfixlength_bad(self):
        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)
        
        payload = copy.deepcopy(self.default_payload)
        payload["biosamples"][0]["anonymous_sample_id"] = "%s-%s" % (settings.ANON_PREFIXES[0] if settings.ANON_PREFIXES else "TEST", "00001") 
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertEqual("anonymous_sample_id must have a postfix of length %s, but received a postfix of length: %s" % (settings.ANON_POSTFIX_LENGTH, 5), "".join(j["messages"][0]["anonymous_sample_id"][0]["message"]))
        assert models.BiosampleArtifact.objects.count() == 0

    def test_add_biosample_anonymous_sample_id_wrongpostfixchars_bad(self):
        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)
        
        for bad_char in ["/", "\\", ".", "#", "%", "$"]:
            payload = copy.deepcopy(self.default_payload)
            payload["biosamples"][0]["anonymous_sample_id"] = "%s-%s" % (settings.ANON_PREFIXES[0] if settings.ANON_PREFIXES else "TEST", "0000" + bad_char + "000") 
            response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
            self.assertEqual(200, response.status_code)
            j = response.json()
            self.assertEqual(j["errors"], 1)
            self.assertEqual("anonymous_sample_id postfix can only contain alphanumeric characters", "".join(j["messages"][0]["anonymous_sample_id"][0]["message"]))
            assert models.BiosampleArtifact.objects.count() == 0


class OAuthEmptyBiosampleArtifactTest(OAuthAPIClientBase):
    def setUp(self):
        super().setUp()

        self.endpoint = reverse("api.artifact.biosample.addempty")

        self.scope = "majora2.force_add_biosampleartifact majora2.add_biosampleartifact majora2.change_biosampleartifact majora2.add_biosourcesamplingprocess majora2.change_biosourcesamplingprocess"
        self.token = self._get_token(self.scope)

        fp = Permission.objects.get(codename="force_add_biosampleartifact")
        self.user.user_permissions.add(fp)
        self.user.save()

        self.full_scope = "majora2.add_biosampleartifact majora2.change_biosampleartifact majora2.add_biosamplesource majora2.change_biosamplesource majora2.add_biosourcesamplingprocess majora2.change_biosourcesamplingprocess"
        self.full_token = self._get_token(self.full_scope)

    def test_put_empty_biosampleartifact_list_single_ok(self):
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                "FORCE-0001",
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        for biosample in payload["biosamples"]:
            assert models.BiosampleArtifact.objects.filter(central_sample_id=biosample).count() == 1

        # Ensure double submit gets ignored
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(len(j["ignored"]), 1)
        self.assertIn("FORCE-0001", j["ignored"][0][2]) # unpack tuple

        # Check the validity endpoint
        payload = {
            "username": "hoot",
            "token": "oauth",
            "biosamples": [
                "FORCE-0001",
            ],
        }
        response = self.c.post(reverse("api.artifact.biosample.query.validity"), payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()

        assert j["result"]["FORCE-0001"]["exists"] == True
        assert j["result"]["FORCE-0001"]["has_sender_id"] == False
        assert j["result"]["FORCE-0001"]["has_metadata"] == False

        # Ensure double submit gets accepted if you try to add a sender_sample_id
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {"central_sample_id": "FORCE-0001", "sender_sample_id": "SECRET-0001"},
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(len(j["ignored"]), 1)
        self.assertIn("FORCE-0001", j["ignored"][0][2]) # unpack tuple

        bs = models.BiosampleArtifact.objects.get(central_sample_id="FORCE-0001")
        assert bs.sender_sample_id == "SECRET-0001"

        # Check the validity endpoint
        payload = {
            "username": "hoot",
            "token": "oauth",
            "biosamples": [
                "FORCE-0001",
            ],
        }
        response = self.c.post(reverse("api.artifact.biosample.query.validity"), payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()

        assert j["result"]["FORCE-0001"]["exists"] == True
        assert j["result"]["FORCE-0001"]["has_sender_id"] == True
        assert j["result"]["FORCE-0001"]["has_metadata"] == False

    def test_put_empty_biosampleartifact_stomp_ok(self):
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                default_central_sample_id,
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        # Hackily stomp a new record over the empty one
        payload = copy.deepcopy(default_payload)
        payload["username"] = "oauth"
        payload["token"] = "oauth"
        response = self.c.post(self.endpoint.replace("addempty", "add"), payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.full_token)
        self.assertEqual(200, response.status_code)

        assert models.BiosampleArtifact.objects.filter(central_sample_id=default_central_sample_id).count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        _test_biosample(self, bs, payload)


    def test_put_empty_biosampleartifact_with_sid_full_stomp_ok(self):
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {"central_sample_id": default_central_sample_id, "sender_sample_id": "SECRET-0001"},
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        # Hackily stomp a new record over the empty one
        payload = copy.deepcopy(default_payload)
        payload["biosamples"][0]["sender_sample_id"] = "DIFFERENT-SECRET"
        payload["username"] = "oauth"
        payload["token"] = "oauth"
        response = self.c.post(self.endpoint.replace("addempty", "add"), payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.full_token)
        self.assertEqual(200, response.status_code)

        assert models.BiosampleArtifact.objects.filter(central_sample_id=default_central_sample_id).count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        _test_biosample(self, bs, payload)

        # Assert it again anyway
        assert bs.sender_sample_id != "SECRET-0001"
        assert bs.sender_sample_id == "DIFFERENT-SECRET"

        # Check the validity endpoint
        payload = {
            "username": "hoot",
            "token": "oauth",
            "biosamples": [
                default_central_sample_id,
            ],
        }
        response = self.c.post(reverse("api.artifact.biosample.query.validity"), payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()

        assert j["result"][default_central_sample_id]["exists"] == True
        assert j["result"][default_central_sample_id]["has_sender_id"] == True
        assert j["result"][default_central_sample_id]["has_metadata"] == True

    def test_put_empty_biosampleartifact_partial_bad(self):
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                default_central_sample_id,
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        # Hackily stomp a new record over the empty one
        payload = copy.deepcopy(default_payload)
        payload["username"] = "oauth"
        payload["token"] = "oauth"
        response = self.c.post(self.endpoint.replace("addempty", "update"), payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.full_token)
        self.assertEqual(200, response.status_code)

        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertIn("Cannot use `partial` on empty BiosampleArtifact", "".join(j["messages"]))

    def test_put_empty_biosampleartifact_sid_partial_bad(self):
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {"central_sample_id": default_central_sample_id, "sender_sample_id": "SECRET-0001"},
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        # Hackily stomp a new record over the empty one
        payload = copy.deepcopy(default_payload)
        payload["username"] = "oauth"
        payload["token"] = "oauth"
        response = self.c.post(self.endpoint.replace("addempty", "update"), payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.full_token)
        self.assertEqual(200, response.status_code)

        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertIn("Cannot use `partial` on empty BiosampleArtifact", "".join(j["messages"]))

        assert models.BiosampleArtifact.objects.filter(central_sample_id=default_central_sample_id).count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.sender_sample_id == "SECRET-0001" # check unchanged

    def test_put_empty_biosampleartifact_list_single_bad_scope_bad(self):
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                "FORCE-0001",
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.tokens["bad_scope"])
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertIn("Your token is valid but does not have all of the scopes to perform this action.", "".join(j["messages"]))

    def test_put_empty_biosampleartifact_list_multi_ok(self):
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                "FORCE-0001",
                "FORCE-0002",
                "FORCE-0003",
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        for biosample in payload["biosamples"]:
            assert models.BiosampleArtifact.objects.filter(central_sample_id=biosample).count() == 1

    def test_put_empty_biosampleartifact_dict_single_ok(self):
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {"central_sample_id": "FORCE-0001", "sender_sample_id": "SECRET-0001"},
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        for biosample in payload["biosamples"]:
            assert models.BiosampleArtifact.objects.filter(central_sample_id=biosample["central_sample_id"]).count() == 1
            sample = models.BiosampleArtifact.objects.get(central_sample_id=biosample["central_sample_id"])
            assert sample.sender_sample_id == biosample["sender_sample_id"]

        # Check the validity endpoint
        payload = {
            "username": "hoot",
            "token": "oauth",
            "biosamples": [
                "FORCE-0001",
            ],
        }
        response = self.c.post(reverse("api.artifact.biosample.query.validity"), payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()

        assert j["result"]["FORCE-0001"]["exists"] == True
        assert j["result"]["FORCE-0001"]["has_sender_id"] == True
        assert j["result"]["FORCE-0001"]["has_metadata"] == False

    def test_put_empty_biosampleartifact_dict_multi_ok(self):
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {"central_sample_id": "FORCE-0001", "sender_sample_id": "SECRET-0001"},
                {"central_sample_id": "FORCE-0002", "sender_sample_id": "SECRET-0002"},
                {"central_sample_id": "FORCE-0003", "sender_sample_id": "SECRET-0003"},
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        for biosample in payload["biosamples"]:
            assert models.BiosampleArtifact.objects.filter(central_sample_id=biosample["central_sample_id"]).count() == 1
            sample = models.BiosampleArtifact.objects.get(central_sample_id=biosample["central_sample_id"])
            assert sample.sender_sample_id == biosample["sender_sample_id"]

    def test_put_empty_biosampleartifact_wrong_dict_bad1(self):
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {"FORCE-0001": {"sender_sample_id": "SECRET-0001"}},
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        j = response.json()
        for biosample in payload["biosamples"]:
            assert models.BiosampleArtifact.objects.filter(central_sample_id="FORCE-0001").count() == 0
        self.assertEqual(j["warnings"], 1)
        self.assertIn("'biosamples' appears malformed", "".join(j["messages"]))

    def test_put_empty_biosampleartifact_wrong_dict_bad2(self):
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {"FORCE-0001": "SECRET-0001"},
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        j = response.json()
        for biosample in payload["biosamples"]:
            assert models.BiosampleArtifact.objects.filter(central_sample_id="FORCE-0001").count() == 0
        self.assertEqual(j["warnings"], 1)
        self.assertIn("'biosamples' appears malformed", "".join(j["messages"]))

    def test_put_empty_biosampleartifact_wrong_type_bad1(self):
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                1.0,
                2,
                [],
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        j = response.json()
        self.assertEqual(j["warnings"], 3)
        self.assertIn("'biosamples' appears malformed", "".join(j["messages"]))

    def test_put_empty_biosampleartifact_wrong_type_bad2(self):
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": "HOOT",
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertIn("'biosamples' appears malformed", "".join(j["messages"]))

    def test_put_empty_biosampleartifact_ignore_ok(self):
        obj = models.BiosampleArtifact.construct_test_object()
        obj.save()

        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                obj.central_sample_id,
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        j = response.json()
        for biosample in payload["biosamples"]:
            assert models.BiosampleArtifact.objects.filter(central_sample_id=obj.central_sample_id).count() == 1

        self.assertEqual(len(j["ignored"]), 1)
        self.assertIn(obj.central_sample_id, j["ignored"][0][2]) # unpack tuple

        obj.delete()
        obj.save()

    def test_put_empty_biosampleartifact_stomp_sid_on_notblank_bad(self):

        # push full sample
        payload = copy.deepcopy(default_payload)
        payload["username"] = "oauth"
        payload["token"] = "oauth"
        response = self.c.post(self.endpoint.replace("addempty", "add"), payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.full_token)
        self.assertEqual(200, response.status_code)

        # stomp it with addempty
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                { "central_sample_id": default_central_sample_id, "sender_sample_id": "NEW-SECRET" },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        # check the addempty stomp has no effect on existing sample
        j = response.json()
        for biosample in payload["biosamples"]:
            assert models.BiosampleArtifact.objects.filter(central_sample_id=default_central_sample_id).count() == 1
            sample = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
            assert sample.sender_sample_id != "NEW-SECRET"

        self.assertEqual(len(j["ignored"]), 1) # ignored because the force fails
        self.assertEqual(len(j["updated"]), 0) # not updated

        tatl = tmodels.TatlRequest.objects.filter(response_uuid=j["request"]).first()
        self.assertIsNotNone(tatl)
        self.assertEqual(tatl.verbs.count(), 0)


    def test_put_empty_biosampleartifact_stomp_sid_ok(self):

        # Push a blank
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                { "central_sample_id": default_central_sample_id },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        # Stomp with a secret
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                { "central_sample_id": default_central_sample_id, "sender_sample_id": "SECRET" },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        # Check the secret exists
        j = response.json()
        for biosample in payload["biosamples"]:
            assert models.BiosampleArtifact.objects.filter(central_sample_id=default_central_sample_id).count() == 1
            sample = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
            assert sample.sender_sample_id == "SECRET"

        self.assertEqual(len(j["ignored"]), 1) # still ignored because the force fails
        self.assertEqual(len(j["updated"]), 1)
        self.assertIn(default_central_sample_id, j["updated"][0][2]) # unpack tuple

        tatl = tmodels.TatlRequest.objects.filter(response_uuid=j["request"]).first()
        self.assertIsNotNone(tatl)

        self.assertEqual(tatl.verbs.count(), 1)
        expected_verbs = [
            ("UPDATE", models.BiosampleArtifact.objects.get(dice_name=default_central_sample_id)),
        ]
        for verb in tatl.verbs.all():
            self.assertIn( (verb.verb, verb.content_object), expected_verbs )


    def test_put_empty_biosampleartifact_stomp_sid_blank_ignored(self):
        # Push a blank with a sender_sample_id
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                { "central_sample_id": default_central_sample_id, "sender_sample_id": "SECRET" },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        # Stomp the blank without a sender_sample_id
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                { "central_sample_id": default_central_sample_id },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        # Check the secret was not stomped over
        j = response.json()
        for biosample in payload["biosamples"]:
            assert models.BiosampleArtifact.objects.filter(central_sample_id=default_central_sample_id).count() == 1
            sample = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
            assert sample.sender_sample_id == "SECRET"

        self.assertEqual(len(j["ignored"]), 1) # still ignored because the force fails
        self.assertEqual(len(j["updated"]), 0)

        tatl = tmodels.TatlRequest.objects.filter(response_uuid=j["request"]).first()
        self.assertIsNotNone(tatl)
        self.assertEqual(tatl.verbs.count(), 0)


    def test_addempty_biosample_tatl(self):
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                "FORCE-0001",
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        j = response.json()

        tatl = tmodels.TatlRequest.objects.filter(response_uuid=j["request"]).first()
        self.assertIsNotNone(tatl)

        self.assertEqual(tatl.verbs.count(), 1)

        expected_verbs = [
            ("CREATE", models.BiosampleArtifact.objects.get(dice_name="FORCE-0001")),
        ]
        for verb in tatl.verbs.all():
            self.assertIn( (verb.verb, verb.content_object), expected_verbs )


    def test_put_empty_biosampleartifact_metadata_ok(self):
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {"central_sample_id": "FORCE-0001", "sender_sample_id": "SECRET-0001", "metadata": {"mytag": {"mykey": "myval"}}},
                {"central_sample_id": "FORCE-0002", "sender_sample_id": "SECRET-0002", "metadata": {}},
                {"central_sample_id": "FORCE-0003"},
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)

        for biosample in payload["biosamples"]:
            assert models.BiosampleArtifact.objects.filter(central_sample_id=biosample["central_sample_id"]).count() == 1
            sample = models.BiosampleArtifact.objects.get(central_sample_id=biosample["central_sample_id"])
            assert sample.get_metadata_as_struct() == biosample.get("metadata", {})
            assert len(sample.get_metadata_as_struct()) == len(biosample.get("metadata", {}))
    
    def test_put_empty_biosampleartifact_put_again_anonymous_sample_id_ok(self):
        # Put, no id
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {"central_sample_id": default_central_sample_id},
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == None

        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        # Re-put, with id
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {"central_sample_id": default_central_sample_id, "anonymous_sample_id" : user_anonymous_sample_id},
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

    def test_put_empty_biosampleartifact_sid_anonymous_sample_id_ok(self):
        # Put, no ids
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {"central_sample_id": default_central_sample_id},
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.sender_sample_id == None
        assert bs.anonymous_sample_id == None

        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        # Put, ids
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {"central_sample_id": default_central_sample_id, "sender_sample_id" : "SECRET-0001", "anonymous_sample_id" : user_anonymous_sample_id},
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.sender_sample_id == "SECRET-0001"
        assert bs.anonymous_sample_id == user_anonymous_sample_id

        # Re-put, no ids
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {"central_sample_id": default_central_sample_id},
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.sender_sample_id == "SECRET-0001"
        assert bs.anonymous_sample_id == user_anonymous_sample_id

    def test_change_empty_biosampleartifact_anonymous_sample_id_ok(self):
        # Put, no id
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {"central_sample_id": default_central_sample_id},
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == None

        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        # Put, with id
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {"central_sample_id": default_central_sample_id, "anonymous_sample_id" : user_anonymous_sample_id},
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

        perm = Permission.objects.get(codename="can_change_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        # Put, changing id
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id, 
                    "anonymous_sample_id" : user_anonymous_sample_id_2,
                },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id_2

    def test_change_empty_biosampleartifact_anonymous_sample_id_null_preserved_ok(self):
        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        # Put, with id
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {"central_sample_id": default_central_sample_id, "anonymous_sample_id" : user_anonymous_sample_id},
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

        # Put, with id key but its empty
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id, 
                    "anonymous_sample_id" : "",
                },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

    def test_put_empty_biosampleartifact_anonymous_sample_id_duplicate_bad(self):
        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id, 
                    "anonymous_sample_id" : user_anonymous_sample_id,
                },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id_2, 
                    "anonymous_sample_id" : user_anonymous_sample_id,
                },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertEqual("Biosample artifact with this Anonymous sample id already exists.", "".join(j["messages"][0]["anonymous_sample_id"][0]["message"]))
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

    def test_change_empty_biosampleartifact_anonymous_sample_id_duplicate_bad(self):
        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id, 
                    "anonymous_sample_id" : user_anonymous_sample_id,
                },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id_2, 
                    "anonymous_sample_id" : user_anonymous_sample_id_2,
                },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 2
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id_2)
        assert bs.anonymous_sample_id == user_anonymous_sample_id_2

        perm = Permission.objects.get(codename="can_change_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id_2, 
                    "anonymous_sample_id" : user_anonymous_sample_id,
                },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertEqual("Biosample artifact with this Anonymous sample id already exists.", "".join(j["messages"][0]["anonymous_sample_id"][0]["message"]))
        assert models.BiosampleArtifact.objects.filter().count() == 2
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id_2)
        assert bs.anonymous_sample_id == user_anonymous_sample_id_2

    def test_put_empty_biosampleartifact_anonymous_sample_id_noperm_bad(self):
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id, 
                    "anonymous_sample_id" : user_anonymous_sample_id,
                },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertEqual("You do not have permission to add the anonymous_sample_id on BiosampleArtifact %s" % default_central_sample_id, "".join(j["messages"][0]))
        assert models.BiosampleArtifact.objects.count() == 0

    def test_change_empty_biosampleartifact_anonymous_sample_id_noperm_bad(self):
        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id, 
                    "anonymous_sample_id" : user_anonymous_sample_id,
                },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

        # ID is the same, no effect
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {  
                    "central_sample_id": default_central_sample_id,
                    "anonymous_sample_id" : user_anonymous_sample_id,
                },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

        # ID is different, rejected
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {  
                    "central_sample_id": default_central_sample_id,
                    "anonymous_sample_id" : user_anonymous_sample_id_2,
                },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertEqual("You do not have permission to change the anonymous_sample_id on BiosampleArtifact %s" % default_central_sample_id, "".join(j["messages"][0]))
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id       

    def test_put_empty_biosampleartifact_anonymous_sample_id_wrongformat_bad(self):
        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {  
                    "central_sample_id": default_central_sample_id,
                    "anonymous_sample_id" : "%s-%s" % (settings.ANON_PREFIXES[0] if settings.ANON_PREFIXES else "TEST", "000-0001") ,
                },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertEqual("anonymous_sample_id must consist of a prefix and postfix, separated by a single '-' character", "".join(j["messages"][0]["anonymous_sample_id"][0]["message"]))
        assert models.BiosampleArtifact.objects.count() == 0

    def test_put_empty_biosampleartifact_anonymous_sample_id_wrongprefix_bad(self):
        if settings.ANON_PREFIXES:
            badprefix = "".join(settings.ANON_PREFIXES) * 2
            perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
            self.user.user_permissions.add(perm)

            payload = {
                "username": self.user.username,
                "token": "oauth",
                "biosamples": [
                    {  
                        "central_sample_id": default_central_sample_id,
                        "anonymous_sample_id" : "%s-%s" % (badprefix, "00000001"),
                    },
                ],
            }
            response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
            self.assertEqual(200, response.status_code)
            j = response.json()
            self.assertEqual(j["errors"], 1)
            self.assertEqual("anonymous_sample_id has an invalid prefix: %s" % badprefix, "".join(j["messages"][0]["anonymous_sample_id"][0]["message"]))
            assert models.BiosampleArtifact.objects.count() == 0
    
    def test_put_empty_biosampleartifact_anonymous_sample_id_wrongpostfixlength_bad(self):
        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)
        
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {  
                    "central_sample_id": default_central_sample_id,
                    "anonymous_sample_id" : "%s-%s" % (settings.ANON_PREFIXES[0] if settings.ANON_PREFIXES else "TEST", "00001") ,
                },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 1)
        self.assertEqual("anonymous_sample_id must have a postfix of length %s, but received a postfix of length: %s" % (settings.ANON_POSTFIX_LENGTH, 5), "".join(j["messages"][0]["anonymous_sample_id"][0]["message"]))
        assert models.BiosampleArtifact.objects.count() == 0

    def test_put_empty_biosampleartifact_anonymous_sample_id_wrongpostfixchars_bad(self):
        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)
        
        for bad_char in ["/", "\\", ".", "#", "%", "$"]:
            payload = {
                "username": self.user.username,
                "token": "oauth",
                "biosamples": [
                    {  
                        "central_sample_id": default_central_sample_id,
                        "anonymous_sample_id" : "%s-%s" % (settings.ANON_PREFIXES[0] if settings.ANON_PREFIXES else "TEST", "0000" + bad_char + "000") ,
                    },
                ],
            }
            response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
            self.assertEqual(200, response.status_code)
            j = response.json()
            self.assertEqual(j["errors"], 1)
            self.assertEqual("anonymous_sample_id postfix can only contain alphanumeric characters", "".join(j["messages"][0]["anonymous_sample_id"][0]["message"]))
            assert models.BiosampleArtifact.objects.count() == 0

    def test_put_empty_then_add_biosampleartifact_anonymous_sample_id_preserved_ok(self):
        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        # Add empty record with id
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id, 
                    "anonymous_sample_id" : user_anonymous_sample_id,
                },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

        # Add full record without id
        payload = copy.deepcopy(default_payload)
        payload["username"] = "oauth"
        payload["token"] = "oauth"
        response = self.c.post(self.endpoint.replace("addempty", "add"), payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.full_token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

        # Add full record with empty id
        payload = copy.deepcopy(default_payload)
        payload["username"] = "oauth"
        payload["token"] = "oauth"
        payload["biosamples"][0]["anonymous_sample_id"] = ""
        response = self.c.post(self.endpoint.replace("addempty", "add"), payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.full_token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

    def test_add_then_put_empty_biosampleartifact_anonymous_sample_preserved_ok(self):
        perm = Permission.objects.get(codename="can_add_anonymous_sample_id")
        self.user.user_permissions.add(perm)

        # Add full record with id
        payload = copy.deepcopy(default_payload)
        payload["username"] = "oauth"
        payload["token"] = "oauth"
        payload["biosamples"][0]["anonymous_sample_id"] = user_anonymous_sample_id
        response = self.c.post(self.endpoint.replace("addempty", "add"), payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.full_token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

        # Add empty record without id
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id, 
                },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

        # Add empty record with empty key
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id, 
                    "anonymous_sample_id" : "",
                },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == user_anonymous_sample_id

    def test_put_empty_biosampleartifact_then_add_default_anonymous_sample_ok(self):
        # Add empty record without id
        payload = {
            "username": self.user.username,
            "token": "oauth",
            "biosamples": [
                {
                    "central_sample_id": default_central_sample_id, 
                },
            ],
        }
        response = self.c.post(self.endpoint, payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == None

        # Add full record without id, one should be generated
        payload = copy.deepcopy(default_payload)
        payload["username"] = "oauth"
        payload["token"] = "oauth"
        response = self.c.post(self.endpoint.replace("addempty", "add"), payload, secure=True, content_type="application/json", HTTP_AUTHORIZATION="Bearer %s" % self.full_token)
        self.assertEqual(200, response.status_code)
        j = response.json()
        self.assertEqual(j["errors"], 0)
        assert models.BiosampleArtifact.objects.count() == 1
        bs = models.BiosampleArtifact.objects.get(central_sample_id=default_central_sample_id)
        assert bs.anonymous_sample_id == default_anonymous_sample_id
