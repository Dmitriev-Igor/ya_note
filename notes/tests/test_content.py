from django.contrib.auth import get_user_model

from .base_test_case import BaseTestCase
from notes.forms import NoteForm

User = get_user_model()


class TestContent(BaseTestCase):

    def test_notes_list_for_users(self):
        test_cases = [
            (self.author_client, True),
            (self.reader_client, False)
        ]

        for client, should_contain in test_cases:
            with self.subTest(client=client):
                response = client.get(self.list_url)
                notes = response.context['object_list']
                result = self.note in notes
                self.assertIs(result, should_contain)

    def test_create_and_add_note_pages_contains_form(self):
        urls = (self.add_url, self.edit_url)
        for url in urls:
            response = self.author_client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
