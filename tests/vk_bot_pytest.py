from vk_bot_folder.functions import get_user_info, get_city, get_age, extract_info, get_photos_info, search_users


class TestFunctions:

    def setup_class(self):
        print('method setup')

    def teardown_class(self):
        print('method teardown')

    def test_get_user_info(self):
        check = get_user_info('write_your_user_id_here')
        assert check is not None and type(check) is dict

    def test_get_city(self):
        check = get_city('Москва')
        assert check is not None and type(check) is int

    def test_get_age(self):
        check = get_age('01.01.2000')
        assert check is not None and type(check) is int

    def test_extract_info(self):
        check = extract_info('write_your_user_id_here', 'Москва', '01.01.2000')
        assert check is not None and type(check) is list and len(check) == 3

    def test_get_photos_info(self):
        check = get_photos_info('write_any_search_user_id_here')  # profile should not be private
        assert check is not None and type(check) is list and len(check) == 3

    def test_search_users(self):
        check = search_users('write_your_user_id_here', 'Москва', '01.01.2000')
        assert check is not None and type(check) is dict and len(check) == 10
