import unittest
import PyTango


class ResourceManagerTestCase(unittest.TestCase):

    def test_ping_non_negative(self):
        device = PyTango.DeviceProxy('test/resource_manager/1')
        self.assertTrue(device.ping() > 0)

    def test_get_resource_water(self):
        device = PyTango.DeviceProxy('test/resource_manager/1')
        expected_result = 'water # consumable # 2017-05-31 07:35:34.433790'
        expected_result += '# 2017-05-31 07:35:34.433790 # 74.443 # 5254.2342'
        self.assertTrue(device.ask_resource("water"), expected_result)

    def test_set_updated_resource_values(self):
        device = PyTango.DeviceProxy('test/resource_manager/1')
        input_string = 'water#consumable#2017-05-31 07:35:34.433790'
        input_string += '#2017-05-31 07:35:34.433790#74.443#5254.2342'
        expected_result = 'SUCCESS'
        received_result = device.set_updated_resource_values(input_string)
        self.assertTrue(received_result, expected_result)


if __name__ == '__main__':
    unittest.main()
