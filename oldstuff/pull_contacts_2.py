#!/usr/bin/env python

import os, sys, getpass
import atom.data, gdata.data, gdata.contacts.client, gdata.contacts.data
from optparse import OptionParser

class GoogleContacts(object):
    def __init__(self, email, password, maxnum=3000):
        gd_client = gdata.contacts.data.ContactsClient(source = 'tanim-islam-cloud-storage-2')
        gd_client.ClientLogin(email, password, gd_client.source)

        query = gdata.contacts.client.ContactsQuery()
        query.max_results = maxnum
        contacts = gd_client.GetContacts(q = query)
        contacts_dict = { entry.title.text : entry for entry in contacts.entry }
        #
        groups = gd_client.GetGroupsFeed(gdata.service.Query(feed='/m8/feeds/groups/default/full').ToUri())
        groups_dict = { gentry.id.text : gentry.title.text for gentry in groups.entry }

        name_dict_map = {}
        for contact_name in sorted(contacts_dict.keys()):
            entry = contacts_dict[contact_name]
            if len(entry.group_membership_info) != 1:
                continue
            group_name = groups_dict[entry.group_membership_info[0].href]
            name_dict_map.setdefault(group_name, []).append(contact_name)

        # for group_name in sorted(name_dict_map.keys()):
        #    print '%s => %d' % (group_name, len(name_dict_map[group_name]))
        # not_group = 'Businesses And Mailing Lists'

        # this is the list of the contacts with their email addresses
        self.gmail_contacts = {}
        # for group_name in [gname for gname in name_dict_map.keys() if gname not in not_group ]:
        for group_name in name_dict_map.keys():
            for contact_name in name_dict_map[group_name]:
                entry = contacts_dict[contact_name]
                for email in entry.email:
                    self.gmail_contacts.setdefault(group_name, {})
                    self.gmail_contacts[group_name].setdefault(contact_name, []).append(email.address)
                # for email in entry.email:
                #     if email.address.endswith('@gmail.com'):
                #         gmail_contacts.setdefault(contact_name, []).append(email.address)
                #     if 'yahoo' in email.address:
                #         gmail_contacts.setdefault(contact_name, []).append(email.address)
                #     if 'hotmail.com' in email.address or 'msn.com' in email.address:
                #        gmail_contacts.setdefault(contact_name, []).append(email.address)

        # print len(gmail_contacts.keys()), sum([ len(gmail_contacts[contact_name]) for 
        #                                        contact_name in gmail_contacts.keys()])
        # for contact_name in sorted(gmail_contacts.keys()):
        #    print '%s => %s' % (contact_name, sorted(gmail_contacts[contact_name]))

        # this is the list of the contacts and their IM addresses
        # print 'NAME OF GMAIL IM INFORMATION'
        self.gmail_im_contacts = {}
        protocols_mapping = { 'http://schemas.google.com/g/2005#GOOGLE_TALK' : 'Google Talk',
                              'http://schemas.google.com/g/2005#YAHOO' : 'Yahoo',
                              'http://schemas.google.com/g/2005#SKYPE' : 'Skype',
                              'http://schemas.google.com/g/2005#JABBER' : 'Jabber',
                              'http://schemas.google.com/g/2005#MSN' : 'MSN',
                              'http://schemas.google.com/g/2005#AIM' : 'AOL',
                              'http://schemas.google.com/g/2005#ICQ' : 'ICQ',
                              'Twitter' : 'Twitter' }
        # for group_name in [gname for gname in name_dict_map.keys() if gname not in not_group ]:
        for group_name in name_dict_map.keys():
            for contact_name in name_dict_map[group_name]:
                entry = contacts_dict[contact_name]
                for im in entry.im:
                    try:
                        protocol_name = protocols_mapping[im.protocol]
                        address = im.address
                        self.gmail_im_contacts.setdefault(group_name, {})
                        self.gmail_im_contacts[group_name].setdefault(contact_name, {})
                        self.gmail_im_contacts[group_name][contact_name].setdefault(protocol_name, []).append(address)
                    except KeyError:
                        f = 5
                # print 'TANIM DEBUG problem with %s and protocol %s' % (contact_name, im.protocol)

        # for contact_name in sorted(gmail_im_contacts.keys()):
        #    print '%s => %s' % (contact_name, gmail_im_contacts[contact_name])

    def print_pine_addresses(self):
        all_contacts_email = { contact_name : self.gmail_contacts[group_name][contact_name] for group_name in self.gmail_contacts.keys() for
                               contact_name in self.gmail_contacts[group_name].keys() }
        for contact_name in sorted(all_contacts_email.keys()):
            for email_address in sorted(all_contacts_email[contact_name]):
                print '%s\t%s\t"%s" <%s>' % ("", contact_name, contact_name, email_address)

    def get_groups(self):
        groups_by_status = {}
        groups_by_status['email'] = sorted(self.gmail_contacts.keys())
        groups_by_status['im'] = sorted(self.gmail_im_contacts.keys())
        
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--email', dest='email', action='store', type=str,
                      help='email address to get google contact info from.')
    parser.add_option('--passwd', dest='passwd', action='store', type=str,
                      help='email address to get google contact info from.')
    options, args = parser.parse_args()
    if options.email is None:
        raise ValueError("Error, must give the email address")
    if options.passwd is None:
        mypasswd = getpass.getpass()
    else:
        mypasswd = options.passwd
        # raise ValueError("Error, must give the password")
    gcontacts = GoogleContacts(options.email, mypasswd)
    gcontacts.print_pine_addresses()

