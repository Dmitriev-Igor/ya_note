from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING
import pytils.translit

User = get_user_model()


class TestNoteCreation(TestCase):
    COMMENT_TEXT = 'Новый текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        
        cls.note = Note.objects.create(
            title='Заголовок',
            text=cls.COMMENT_TEXT,
            slug='slug',
            author=cls.author
        )

        cls.url = reverse('notes:add')

        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_can_create_note(self):
        response = self.author_client.post(self.url, data=self.form_data)

        self.assertRedirects(response, reverse('notes:success'))

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)

        new_note = Note.objects.last()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_slug_uniqueness(self):
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_slug_auto_generation(self):
        del self.form_data['slug'] 
        response = self.author_client.post(self.url, data=self.form_data)

        self.assertRedirects(response, reverse('notes:success'))

        new_note = Note.objects.last()
        expected_slug = pytils.translit.slugify(self.form_data['title'])

        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))

        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.reader_client.post(url, self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.author_client.post(url)

        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.reader_client.post(url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
