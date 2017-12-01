from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create default user groups'

    def handle(self, *args, **options):
        free_group, _ = Group.objects.get_or_create(name='Free group')
        basic_group, _ = Group.objects.get_or_create(name='Basic group')
        professional_group, _ = Group.objects.get_or_create(name='Professional group')
        enterprise_group, _ = Group.objects.get_or_create(name='Enterprise group')

        perm_advanced_config = Permission.objects.get(codename='can_access_advanced_configuration')
        perm_segment_notifications = Permission.objects.get(codename='can_segment_notifications')
        perm_autoresponder = Permission.objects.get(codename='can_use_autoresponder')
        perm_timed_messaged = Permission.objects.get(codename='can_use_timed_messages')
        perm_advanced_triggers = Permission.objects.get(codename='can_use_advanced_triggers')

        basic_group.permissions.add(perm_advanced_config)

        professional_group.permissions.add(perm_advanced_config)
        professional_group.permissions.add(perm_segment_notifications)
        professional_group.permissions.add(perm_autoresponder)

        enterprise_group.permissions.add(perm_advanced_config)
        enterprise_group.permissions.add(perm_segment_notifications)
        enterprise_group.permissions.add(perm_autoresponder)
        enterprise_group.permissions.add(perm_timed_messaged)
        enterprise_group.permissions.add(perm_advanced_triggers)

