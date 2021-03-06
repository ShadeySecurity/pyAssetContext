@auth.requires_login()
@auth.requires_membership('import')
def index():
    #Import needed libraries and admin modules
    import importlib
    from pyloadmodules import find_modules
    from datetime import datetime
    # Load a list of modules
    modsdict = find_modules('../modules')
    module2use = ''
    # Validate the return
    if type(modsdict) is not dict:
        return
    scantypes = []
    # Load modules and put their display names into a list
    for module in modsdict:
        if "EXECUTE" in modsdict[module]['Functions'] and modsdict[module]['Disable'] == False:
            # Update web form
            scantypes.append(modsdict[module]['Display_Name'])
            break
    # Generate the initial form
    webform = SQLFORM.factory(Field(" ", default=" ", writable=False),
                   Field("User_Name", 'string', required=True, default=auth.user.username, requires=IS_NOT_EMPTY(),writable=False),
                   Field('User_IP','string', required=True, writable=False, default=request.client,requires=IS_IPV4()),
                   Field('Scanner_IP','string', default='127.0.0.1', requires=IS_IPV4()),
                   Field('Scan_Type', required=True, requires=IS_IN_SET(scantypes, zero=T("Select Scan Type"), error_message=T('Not a valid option. Please see documentation.'))),
                   Field('Scan_Destinations','list:string',required=True,requires=IS_NOT_EMPTY()),
                   Field('Task_ID', 'string'),
                   Field('Approver', 'string'),
                   Field('Description','text'),
                   Field('Justification','text',required=True, requires=IS_NOT_EMPTY()),
                   submit_button='Import'
                  )
    # Once you select the scan type, we modify the form if the module requests it
    if webform.vars.Scan_Type != "Select Scan Type" and webform.vars.Scan_type != "":
        for module in modsdict:
            if webform.vars.Scan_Type == modsdict[module]["Display_Name"] and modsdict[module]['Disable'] == False:
                module2use = module
                break
        # Import Module
        importmodule = __import__ (module2use)
        # Load it as an object to use
        classmodule = getattr(importmodule,str(module2use))
        # Use the object call
        modsdict[module2use]["Fields"].update(classmodule.execute_fields)
        # TODO: Validate values passed in
        # Load module specific fields
        for field in  modsdict[module2use]["Fields"]:
            webform.append(Field(modsdict[module2use]["Fields"][field]["Name"],modsdict[module2use]["Fields"][field]["Type"],required=modsdict[module2use]["Fields"][field]["Required"], requires=modsdict[module2use]["Fields"][field]["Requires"], default=modsdict[module2use]["Fields"][field]["Default_Value"]))
    # Once submitted by user, now start to do stuff
    if webform.process().accepted:
        # Let the user know we are beginning to execute
        response.flash = T('Scan is being executed and processed! Hold tight.')        
        # We set the defaults for datadict
        datadict = {"user_name":str(form.vars.User_Name), "scan_type": str(form.vars.Scan_Type), "user_ip": str(form.vars.User_IP), "scanner_ip":str(form.vars.Scanner_IP), "approver":str(form.vars.Approver), "description":str(form.vars.Description), "justification":str(form.vars.Justification), "task_id":str(form.vars.Task_ID), "date_timestamp":str(datetime.utcnow()), "network": form.vars.Scan_Destinations}        
        # Determine next insert's ID number
        scan_id = db.scans.id.max() + 1
        if scan_id < 10:
            scan_id = "000%s" % scan_id
        elif scan_id < 100:
            scan_id = "00%s" % scan_id
        elif scan_id < 1000:
            scan_id = "0%s" % scan_id
        else:
            scan_id = "%s" % scan_id
        # Determine the SCAN ID
        scan_id = "%s-%s" % (form.vars.Scan_Typ,scan_id)
        # Now we execute the scan
        try:
            if not modsdict[module2use]['Disable'] and modsdict[module2use]['User_Privileged']:
                # TODO: once I have the execute_helper script re-written, insert interaction here
                pass
            else:
                datadict.update(classmodule.execute(webform.vars))
        except Exception as err:
                response.flash = T("Error while executing scan! Error: %s" % err)
        # Now we submit results to the database
        db.scans.bulk_insert(datadict['scans'])
        #TODO add the rest of the databases
    elif form.errors:
        response.flash = T("Form has errors %s" % error_message)
    else:
        response.flash = T('Please fill out the required information.')
    return dict(form=webform)
