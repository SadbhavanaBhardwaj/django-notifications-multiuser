``django-notifications-multiuser`` Documentation
=======================================


The major difference between ``django-notifications-multiuser`` and ``django-notifications``:

* ``django-notifications`` is for building something like Github "Notifications" which creates one notification object per recipient
* While ``django-notifications_multiuser`` can create one notification object for multiple users

Notifications are actually actions events, which are categorized by four main components.

* ``Actor``. The object that performed the activity.
* ``Verb``. The verb phrase that identifies the action of the activity.
* ``Action Object``. *(Optional)* The object linked to the action itself.
* ``Target``. *(Optional)* The object to which the activity was performed.

``Actor``, ``Action Object`` and ``Target`` are ``GenericForeignKeys`` to any arbitrary Django object.
An action is a description of an action that was performed (``Verb``) at some instant in time by some ``Actor`` on some optional ``Target`` that results in an ``Action Object`` getting created/updated/deleted.

For example: `justquick <https://github.com/justquick/>`_ ``(actor)`` *closed* ``(verb)`` `issue 2 <https://github.com/justquick/django-activity-stream/issues/2>`_ ``(action_object)`` on `activity-stream <https://github.com/justquick/django-activity-stream/>`_ ``(target)`` 12 hours ago

Nomenclature of this specification is based on the Activity Streams Spec: `<http://activitystrea.ms/specs/atom/1.0/>`_

Requirements
============

- Python 3.5, 3.6, 3.7, 3.8
- Django 2.2, 3.0





Notification object Creation
============================

- We are making use of signals to create notification object.
    'notify' signal takes 'recipient', 'actor', 'verb', 'action_object', 'target', 'description', 'timestamp', 'level' as arguments.
    ``notify.send(sender=user, recipient=<User Queryset>, verb="testing notification")``


Notification object Serialization
=================================
    Just like other objects, we can serialize the notification objects.
    Since, the recipient is ManyToManyField, we'll need a nested serializer
    Check the below link for nested serializer
    <https://www.django-rest-framework.org/api-guide/relations/#manytomanyfields-with-a-through-model>
        

API
===

- /api_url/all_list/
    the API accepts GET request and sends list of all the notifications associated with the authenticated user

- /api_url/all_count/
    the API accepts GET request and sends the total count of notification objects corresponding to the authenticated user as response

- /api_url/delete/<slug_id>/
    deletes the notification object for the corresponding slug_id