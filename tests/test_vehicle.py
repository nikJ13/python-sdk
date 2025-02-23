import unittest
import smartcar
import requests
import responses
import json

import dateutil.parser


class TestVehicle(unittest.TestCase):
    def setUp(self):
        self.access_token = 'access_token'
        self.vehicle_id = 'vehicle_id'
        self.vehicle = smartcar.Vehicle(self.vehicle_id, self.access_token)
        self.auth = 'Bearer ' + self.access_token

    def queue(self, method, endpoint, body=None, query=None, headers=None):
        """ queue a mock response """
        url = '/'.join((smartcar.const.API_URL, 'vehicles',
                        self.vehicle_id, endpoint))
        if query:
            query_string = '&'.join(
                k + '=' + str(v) for k, v in query.items()
            )
            url += '?' + query_string
        if not body:
            body = {}
        if not headers:
            headers = {}

        responses.add(method, url,
                      json=body,
                      match_querystring=bool(query),
                      headers=headers)

    def check(self, actual, **kwargs):
        """
        test that the 'Authorization' header is the correct bearer auth string,
        and that each key in the request body is correct.
        """

        self.assertEqual(len(responses.calls), 1)

        request = responses.calls[0].request
        request_auth = request.headers['Authorization']
        self.assertEqual(request_auth, self.auth)

        if kwargs:
            request_json = json.loads(request.body.decode('utf-8'))
            for k, v in kwargs.items():
                self.assertEqual(request_json[k], v)

    @responses.activate
    def test_unit_system(self):
        age = '2018-04-30T22:28:52+00:00'
        self.queue('GET', 'odometer', headers={
            'sc-unit-system': 'metric',
            'sc-data-age': age,
        })
        self.vehicle.odometer()
        headers = responses.calls[0].request.headers
        unit_system = headers['sc-unit-system']
        self.assertEqual(unit_system, 'metric')

        self.queue('GET', 'odometer', headers={
            'sc-unit-system': 'imperial',
            'sc-data-age': age,
        })
        self.vehicle.set_unit_system('imperial')
        self.vehicle.odometer()
        headers = responses.calls[1].request.headers
        unit_system = headers['sc-unit-system']
        self.assertEqual(unit_system, 'imperial')

    @responses.activate
    def test_permission(self):
        data = {
            "permissions": ["read_odometer"]
        }

        self.queue('GET', 'permissions', data)
        response = self.vehicle.permissions()

        self.check(response)
        self.assertEqual(response, data['permissions'])

    @responses.activate
    def test_has_permissions(self):
        data = {
            "permissions": ["read_odometer" , "read_vehicle_info"]
        }

        self.queue('GET', 'permissions', data)
        single_response = self.vehicle.has_permissions("read_odometer")
        required_response = self.vehicle.has_permissions("required:read_odometer")
        multi_response = self.vehicle.has_permissions(["read_odometer", "required:read_vehicle_info"])
        false_response = self.vehicle.has_permissions("read_location")
        false_multi_response = self.vehicle.has_permissions(["read_odometer", "read_location"])

        self.assertTrue(single_response)
        self.assertTrue(required_response)
        self.assertTrue(multi_response)
        self.assertFalse(false_response)
        self.assertFalse(false_multi_response)

    @responses.activate
    def test_info(self):
        data = {
            "id": "36ab27d0-fd9d-4455-823a-ce30af709ffc",
            "make": "TESLA",
            "model": "Model S",
            "year": 2014
        }

        self.queue('GET', '', body=data)
        response = self.vehicle.info()

        self.check(response)
        self.assertEqual(response, data)

    @responses.activate
    def test_location(self):
        data = {
            'latitude': 37.4292,
            'longitude': 122.1381
        }

        age = '2018-04-30T22:28:52+00:00'
        self.queue('GET', 'location', body=data, headers={'sc-data-age': age})
        response = self.vehicle.location()

        self.check(response)
        self.assertEqual(response['data'], data)
        self.assertEqual(response['age'], dateutil.parser.parse(age))

    @responses.activate
    def test_odometer(self):
        data = {
            'odometer': 1234
        }

        age = '2018-04-30T22:28:52+00:00'
        self.queue('GET', 'odometer', body=data, headers={
            'sc-unit-system': 'metric',
            'sc-data-age': age,
        })
        response = self.vehicle.odometer()

        self.check(response)
        self.assertEqual(response['data'], data)
        self.assertEqual(response['unit_system'], 'metric')
        self.assertEqual(response['age'], dateutil.parser.parse(age))

    @responses.activate
    def test_fuel(self):
        data = {
            'range': 1234,
            'percentRemaining': 0.43,
            'amountRemaining': 7
        }

        age = '2018-04-30T22:28:52+00:00'
        self.queue('GET', 'fuel', body=data, headers={
            'sc-unit-system': 'metric',
            'sc-data-age': age,
        })
        response = self.vehicle.fuel()

        self.check(response)
        self.assertEqual(response['data'], data)
        self.assertEqual(response['unit_system'], 'metric')
        self.assertEqual(response['age'], dateutil.parser.parse(age))

    @responses.activate
    def test_tire_pressure(self):
        data = {
            'frontLeft': 227.34,
            'frontRight': 227.34,
            'backLeft': 227.34,
            'backRight': 227.34,
        }

        age = '2018-04-30T22:28:52+00:00'
        self.queue('GET', 'tires/pressure', body=data, headers={
            'sc-unit-system': 'metric',
            'sc-data-age': age,
        })
        response = self.vehicle.tire_pressure()

        self.check(response)
        self.assertEqual(response['data']['tires'], data)
        self.assertEqual(response['unit_system'], 'metric')
        self.assertEqual(response['age'], dateutil.parser.parse(age))

    @responses.activate
    def test_oil(self):
        data = {
            'lifeRemaining': 0.86
        }

        age = '2018-04-30T22:28:52+00:00'
        self.queue('GET', 'engine/oil', body=data, headers={
            'sc-data-age': age,
        })
        response = self.vehicle.oil()

        self.check(response)
        self.assertEqual(response['data'], data)
        self.assertEqual(response['age'], dateutil.parser.parse(age))

    @responses.activate
    def test_battery(self):
        data = {
            'range': 1234,
            'percentRemaining': 0.43,
        }

        age = '2018-04-30T22:28:52+00:00'
        self.queue('GET', 'battery', body=data, headers={
            'sc-unit-system': 'metric',
            'sc-data-age': age,
        })
        response = self.vehicle.battery()

        self.check(response)
        self.assertEqual(response['data'], data)
        self.assertEqual(response['unit_system'], 'metric')
        self.assertEqual(response['age'], dateutil.parser.parse(age))

    @responses.activate
    def test_charge(self):
        data = {
            'isPluggedIn': True,
            'state': 'CHARGING',
        }

        age = '2018-04-30T22:28:52+00:00'
        self.queue('GET', 'charge', body=data, headers={
            'sc-data-age': age,
        })
        response = self.vehicle.charge()

        self.check(response)
        self.assertEqual(response['data'], data)
        self.assertEqual(response['age'], dateutil.parser.parse(age))

    @responses.activate
    def test_vin(self):
        data = {'vin': 'fakeVin'}
        self.queue('GET', 'vin', body=data)

        response = self.vehicle.vin()
        self.check(response)
        self.assertEqual(response, data['vin'])

    @responses.activate
    def test_disconnect(self):
        self.queue('DELETE', 'application')
        self.check(self.vehicle.disconnect())

    @responses.activate
    def test_lock(self):
        data = {
            'status': 'success'
        }
        self.queue('POST', 'security', body=data)

        response = self.vehicle.lock()
        self.check(response, action='LOCK')
        self.assertEqual(response['status'], data['status'])

    @responses.activate
    def test_unlock(self):
        data = {
            'status': 'success'
        }
        self.queue('POST', 'security', body=data)

        response = self.vehicle.unlock()
        self.check(response, action='UNLOCK')
        self.assertEqual(response['status'], data['status'])

    @responses.activate
    def test_batch(self):
        headers = {'sc-unit-system': 'imperial'}
        paths = ['/odometer', '/transmission/fluid', '/fuel', '/sunroof']
        requests = [{"path" : path} for path in paths]
        request_body = {
            "headers" : headers,
            "requests" : requests
        }
        expected_response = {
            "responses": [
                {
                    "headers": headers,
                    "path": '/odometer',
                    "code": 200,
                    "body": {
                        "distance": 32768
                    }
                },
                {
                    "headers": headers,
                    "path": '/transmission/fluid',
                    "code": 200,
                    "body": {
                        "temperature": 98.2,
                        "wear": 0.5
                    }
                },
                {
                    "headers": headers,
                    "path": '/fuel',
                    "code": 200,
                    "body": {
                        "range": 550.8499755859375,
                        "percentRemaining": 0.9449999928474426
                    }
                },
                {
                    "headers": headers,
                    "path": '/sunroof',
                    "code": 501,
                    "body": {
                        "error": 'vehicle_not_capable_error',
                        "message": 'Vehicle is not capable of performing request.'
                    }
                }
            ]
        }
        self.queue('POST', 'batch', body=expected_response)

        response = self.vehicle.batch(paths)

        self.assertEqual(response['responses'], expected_response['responses'])
