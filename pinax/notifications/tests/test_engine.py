import base64

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.utils.six.moves import cPickle as pickle
from pinax.notifications.engine import send_all

from . import get_backend_id
from ..models import (
    NoticeQueueBatch,
    NoticeSetting,
    NoticeType,
    send
)


class BaseTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("test_user", "test@user.com", "123456")
        self.user2 = get_user_model().objects.create_user("test_user2", "test2@user.com", "123456")
        self.user3 = get_user_model().objects.create_user("test_user3", "test3@user.com", "123456")
        NoticeType.create("label", "display", "description")
        self.notice_type = NoticeType.objects.get(label="label")

    def tearDown(self):
        self.user.delete()
        self.user2.delete()
        self.user3.delete()
        self.notice_type.delete()


    @override_settings(SITE_ID=1)
    def test_send_all(self):
        users = [self.user, self.user2, self.user3]

        email_id = get_backend_id("email")
        ns = NoticeSetting.objects.create(
            user=self.user,
            notice_type=self.notice_type,
            medium=email_id,
            send=True
        )
        ns2 = NoticeSetting.objects.create(
            user=self.user2,
            notice_type=self.notice_type,
            medium=email_id,
            send=True
        )

        send(users, "label", queue=True)
        self.assertEqual(NoticeQueueBatch.objects.count(), 1)
        batch = NoticeQueueBatch.objects.all()[0]
        notices = pickle.loads(base64.b64decode(batch.pickled_data))
        self.assertEqual(len(notices), 3)

        send_all()
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(self.user.email, mail.outbox[0].to)
        self.assertIn(self.user2.email, mail.outbox[1].to)
        self.assertNotIn(self.user3.email, mail.outbox[0].to)
        self.assertNotIn(self.user3.email, mail.outbox[1].to)

        ns.delete()
        ns2.delete()
