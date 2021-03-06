import unittest
from unittest.mock import patch
from copy import deepcopy

from app.main import create_app
from tests.fixtures.mock_decision import mock_response, mock_response_900
from tests.fixtures.mock_placements import mock_placements


class TestApp(unittest.TestCase):
    """
    TODO: find a way to create a mocked response from Geo
    so that we can test the response with spocs targeted to a specific location
    """
    mock_response_map = {'default': [mock_response]}
    mock_placement_map = {'top-sites': [mock_response], 'text-promo': [mock_response_900]}

    @classmethod
    def create_client_no_geo_locs(cls):
        app = create_app()
        app.config['TESTING'] = True
        return app.test_client()

    @classmethod
    def get_request_body(cls, without=None, placements=None):
        ret = {
            "version": "1",
            "consumer_key": "12345-test-consumer-key",
            "pocket_id": "{12345678-1234-5678-90ab-1234567890ab}"
        }
        if placements:
            ret['placements'] = placements
        if without:
            ret.pop(without)
        return ret


    """
    Tests: Pulse
    """

    @patch('provider.geo_provider.GeolocationProvider.__init__', return_value=None)
    def test_app_pulse(self, mock_geo):
        resp = self.create_client_no_geo_locs().get('/pulse')
        self.assertEqual(resp.json, {"pulse" : "ok"})

    """
    Tests: spocs
    """

    @patch('provider.geo_provider.GeolocationProvider.__init__', return_value=None)
    @patch('adzerk.api.Api.get_decisions', return_value=mock_response_map)
    def test_app_spocs_production_valid(self, mock_geo, mock_adzerk):
        resp = self.create_client_no_geo_locs().post('/spocs', json=self.get_request_body())
        self.assertEqual(resp.status_code, 200)

    @patch('provider.geo_provider.GeolocationProvider.__init__', return_value=None)
    @patch('adzerk.api.Api.get_decisions', return_value=mock_response_map)
    def test_app_spocs_production_invalid_no_version(self, mock_geo, mock_adzerk):
        resp = self.create_client_no_geo_locs().post('/spocs', json=self.get_request_body(without='version'))
        self.assertEqual(resp.status_code, 400)

    @patch('provider.geo_provider.GeolocationProvider.__init__', return_value=None)
    @patch('adzerk.api.Api.get_decisions', return_value=mock_response_map)
    def test_app_spocs_production_invalid_no_pocket_id(self, mock_geo, mock_adzerk):
        resp = self.create_client_no_geo_locs().post('/spocs', json=self.get_request_body(without='pocket_id'))
        self.assertEqual(resp.status_code, 400)

    @patch('provider.geo_provider.GeolocationProvider.__init__', return_value=None)
    @patch('adzerk.api.Api.get_decisions', return_value=mock_response_map)
    def test_app_spocs_production_invalid_no_consumer_key(self, mock_geo, mock_adzerk):
        resp = self.create_client_no_geo_locs().post('/spocs', json=self.get_request_body(without='consumer_key'))
        self.assertEqual(resp.status_code, 400)

    @patch('provider.geo_provider.GeolocationProvider.__init__', return_value=None)
    @patch('adzerk.api.Api.get_decisions', return_value=mock_response_map)
    def test_app_spocs_production_invalid_pocket_id(self, mock_geo, mock_adzerk):
        data = self.get_request_body()
        data['pocket_id'] = 'invalid'
        resp = self.create_client_no_geo_locs().post('/spocs', json=data)
        self.assertEqual(resp.status_code, 400)

    @patch('provider.geo_provider.GeolocationProvider.__init__', return_value=None)
    @patch('adzerk.api.Api.get_decisions', return_value=mock_response_map)
    def test_app_spocs_production_unrecognized_field(self, mock_geo, mock_adzerk):
        data = self.get_request_body()
        data['invalid'] = 'something'
        resp = self.create_client_no_geo_locs().post('/spocs', json=data)
        self.assertEqual(resp.status_code, 400)

    @patch('provider.geo_provider.GeolocationProvider.__init__', return_value=None)
    @patch('adzerk.api.Api.get_decisions', return_value=mock_response_map)
    def test_app_spocs_production_invalid_content_type(self, mock_geo, mock_adzerk):
        resp = self.create_client_no_geo_locs().post(
            '/spocs',
            headers={'Content-Type': 'text'},
            data=self.get_request_body()
        )
        self.assertEqual(resp.status_code, 400)

    @patch('provider.geo_provider.GeolocationProvider.__init__', return_value=None)
    @patch('adzerk.api.Api.get_decisions', return_value=mock_response_map)
    def test_app_spocs_staging_production_valid(self, mock_geo, mock_adzerk):
        """
        This test would be more useful if we checked that we got different responses based on the site.
        But currently not sure how to return a mocked response based on site, or even to test
        :param mock_geo:
        :param mock_adzerk:
        :return:
        """
        resp = self.create_client_no_geo_locs().post('/spocs?site=12345', json=self.get_request_body())
        self.assertEqual(resp.status_code, 200)

    @patch('provider.geo_provider.GeolocationProvider.__init__', return_value=None)
    def test_app_spocs_production_valid_placements(self, mock_geo):
        resp = self.create_client_no_geo_locs().post('/spocs', json=self.get_request_body(placements=mock_placements))
        self.assertEqual(200, resp.status_code)

    @patch('provider.geo_provider.GeolocationProvider.__init__', return_value=None)
    def test_app_spocs_production_invalid_placement_name(self, mock_geo):
        bad_placements = deepcopy(mock_placements)
        bad_placements[0].pop('name')
        resp = self.create_client_no_geo_locs().post('/spocs', json=self.get_request_body(placements=bad_placements))
        self.assertEqual(400, resp.status_code)

    @patch('provider.geo_provider.GeolocationProvider.__init__', return_value=None)
    def test_app_spocs_production_unknown_placement_field(self, mock_geo):
        bad_placements = deepcopy(mock_placements)
        bad_placements[0]['adTypess'] = ['test']
        resp = self.create_client_no_geo_locs().post('/spocs', json=self.get_request_body(placements=bad_placements))
        self.assertEqual(400, resp.status_code)

    @patch('provider.geo_provider.GeolocationProvider.__init__', return_value=None)
    @patch('adzerk.api.Api.get_decisions', return_value=mock_placement_map)
    def test_app_spocs_production_valid_placements_call(self, mock_geo, mock_dec):
        bad_placements = deepcopy(mock_placements)
        resp = self.create_client_no_geo_locs().post('/spocs', json=self.get_request_body(placements=bad_placements))
        self.assertEqual(200, resp.status_code)
        result = resp.json
        self.assertTrue('top-sites' in result)
        self.assertEqual(1000, result['top-sites'][0]['campaign_id'])
        self.assertEqual('title 1000', result['top-sites'][0]['title'])
        self.assertTrue('text-promo' in result)
        self.assertEqual(900, result['text-promo'][0]['campaign_id'])
        self.assertEqual('title 900', result['text-promo'][0]['title'])
