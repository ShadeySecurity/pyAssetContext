# -*- coding: utf-8 -*-
# try something like
@auth.requires_login()
@auth.requires_membership('editor')
def index():
    # Determine tables
    tables = []
    for item in db.tables():
        tables.append(item)
    # Request which tables to edit
    webform = SQLFORM.factory(Field(" ", default=" ", writable=False),
                   Field("User_Name", 'string', required=True, default=auth.user.username, requires=IS_NOT_EMPTY(),writable=False),
                   Field('User_IP','string', required=True, writable=False, default=request.client,requires=IS_IPV4()),
                   Field('tables', required=True, requires=IS_IN_SET(tables, zero=T("Select Table"), error_message=T('Not a valid option. Please see documentation.'))),
                   Field('Task_ID', 'string'),
                   Field('Approver', 'string'),
                   Field('Description','text'),
                   Field('Justification','text',required=True, requires=IS_NOT_EMPTY()),
                   submit_button='Execute'
                  )
    # display correct form
    if webform.process().accepted and webform.vars.tables != "Select Table" and webform.vars.tables != "":
        if webform.vars.tables in db.tables():
            webform = SQLFORM.smartgrid(db[webform.vars.tables])
        else:
            response.flash = T("I don't know that database, sorry!")
    '''
    if selection == "software":
        grid = SQLFORM.smartgrid(db.software)
    elif selection == "scans":
        grid = SQLFORM.smartgrid(db.scans)
    elif selection == "hops":
        grid = SQLFORM.smartgrid(db.hops, headers={'hops.ip': 'Hop IP', 'hops.hostname': 'Hop Hostname',
                                                  'hops.scanner_ip': 'Origin Host IP',
                                                  'hops.dst_ip': 'Target IP', 'hops.rtt': 'Time to Hop Host (RTT)',
                                                  'hops.ttl': 'Distance from Origin (TTL)'})
    elif selection == "hosts":
        grid = SQLFORM.smartgrid(db.hosts)
    elif selection == "hostname":
        grid = SQLFORM.smartgrid(db.hostname)
    elif selection == "ports":
        grid = SQLFORM.smartgrid(db.ports)
    elif selection == "software_auth":
        grid = SQLFORM.smartgrid(db.software_auth)
    elif selection == "vulnerabilities":
        grid = SQLFORM.smartgrid(db.vulnerabilities)
    elif selection == "interfaces":
        grid = SQLFORM.smartgrid(db.interfaces)
    elif selection == "vlans":
        grid = SQLFORM.smartgrid(db.vlans)
    elif selection == "routes":
        grid = SQLFORM.smartgrid(db.routes)
    elif selection == "host_users":
        grid = SQLFORM.smartgrid(db.host_users)
    elif selection == "auth_groups":
        grid = SQLFORM.smartgrid(db.auth_groups)
    elif selection == "fw_acl":
        grid = SQLFORM.smartgrid(db.fw_acl)
    elif selection == "ssids":
        grid = SQLFORM.smartgrid(db.ssids)
    elif selection == "auth_server":
        grid = SQLFORM.smartgrid(db.auth_server)
    elif selection == "dist_systems":
        grid = SQLFORM.smartgrid(db.dist_systems)
    else:
        response.flash = T("I don't know that database, sorry!")
    '''
    return dict(form=webform)
