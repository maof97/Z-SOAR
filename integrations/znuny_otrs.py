# Integration for Z-SOAR
# Created by: Martin Offermann
#
# This module is used to integrate Z-SOAR with Znuny (formally known as 'OTRS', but from here only called 'Znuny') Webservices.
# It enables Z-SOAR playbooks to use the Znuny Ticketsystem to create tickets and/or add notes to them.
#
# Although this module is a core component of Z-SOAR (cause for the 'Z' in the first place), it is internally handled as an integration,
# because in the future it may be possible to use other ticket systems as well.
# As this is also a 'normal' integration, it can be used to get new detections from Znuny into Z-SOAR and not only the other way around.
# It is also posssible to get context from Znuny into Z-SOAR (e.g. ticket information or using the ITSM CMDB).
#
# Integration Version: 0.0.1 
#
# This module is (currently) capable of:
# [X] Ticketing: Ticket creation
# [ ] Ticketing: Adding notes to tickets
# [ ] Providing new detections.
# [ ] Providing context for detections of type [ContextDevice]
# [X] User interactive setup
#



# This module is heavily using the 'pyOTRS' library. Thanks to @frennkie
import pyotrs

import sys
from lib.config_helper import Config
from lib.logging_helper import Log

cfg = Config().cfg
log_level_file = cfg["integrations"]["znuny_otrs"]["logging"]["log_level_file"]
log_level_stdout = cfg["integrations"]["znuny_otrs"]["logging"]["log_level_stdout"]
mlog = Log("integrations.znuny_otrs", log_level_file, log_level_stdout)

def main():
    # Check if argumemnt 'setup' was passed to the script
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        zs_integration_setup()
    elif len(sys.argv) > 1:
        print("Unknown argument: " + sys.argv[1])
        print("Usage: python3 " + sys.argv[0] + " --setup")
        sys.exit(1)


def zs_integration_setup(zsoar_main_call=False):
    # Import here because this is only needed for setup
    from lib.config_helper import setup_integration as set_int
    from lib.config_helper import setup_ask
    import tests.integrations.test_znuny_otrs as test_znuny_otrs

    intgr = "znuny_otrs"

    if not zsoar_main_call:
        print("This script will setup the integration 'Znuny/OTRS' (from here called just 'Znuny') for Z-SOAR.")
        print("Please enter the required information below.")
        print("")

    set_int(intgr, "url", "url", "Enter the URL to connec to to Znuny", additional_info="Example: https://tickets.example.com")

    set_int(intgr, "webservice_name", "str", "Enter the WebService name to use. E.g. GenericTicketConnectorREST")
    set_int(
        intgr,
        "username",
        "str",
        "Enter the Znuny username",
        additional_info="Be aware that this user needs access to create tickets to the selected queues.",
    )

    set_int(intgr, "password", "secret", "Enter the Znuny password for the user")

    set_int(
        intgr,
        "verify_certs",
        "y/n",
        "Verify Znuny certificates?",
        additional_info="If set to 'n', the connection will be insecure, but you can use self-signed certificates.",
    )

    set_int(intgr, "logging", "log_level", "Enter the log level to stdout", sub_config="log_level_stdout")

    set_int(intgr, "logging", "log_level", "Enter the log level to file", sub_config="log_level_file")

    set_int(intgr, "logging", "log_level", "Enter the log level to syslog", sub_config="log_level_syslog")

    set_int(intgr, "ticketing", "y/n", "Enable creating/adding to tickets in Znuny?", sub_config="enabled")

    set_int(
        intgr,
        "ticketing",
        "str",
        "Enter the name of the target queue to create tickets in",
        sub_config="target_queue",
        additional_info="Be aware that the user needs access to create tickets in this queue.",
    )

    set_int(intgr, "detection_provider", "y/n", "Enable providing new detections FROM Znuny?", sub_config="enabled")

    set_int(
        intgr,
        "detection_provider",
        "str",
        "Enter the name of the source queue to get new detections from",
        sub_config="source_queue",
        additional_info="Be aware that the user needs access to read tickets in this queue.",
    )

    set_int(intgr, "context_provider", "y/n", "Enable providing context from Znuny?", sub_config="enabled")

    set_int(
        intgr,
        "context_provider",
        "str",
        "Enter the name of the source queue to get context from",
        sub_config="itsm_customer",
        additional_info="Be aware that the user needs access to read tickets of this customer.",
    )

    print("")
    print("")
    print("Do you want to test the integration before enabling it?")
    test_now = setup_ask("y", available_responses_list=["y", "n"])
    if test_now == "y":
        print("Testing the integration...")
        result = test_znuny_otrs.test_zs_provide_new_detections()
        if result:
            print("Test successful!")
        else:
            print("Test failed!")
            print("Please check the log file for more information.")
            print("Please fix the issue and try again.")
            print("NOTICE: Not enabling the integration because the test failed.")
            sys.exit(1)

    set_int(intgr, "enabled", "y/n", message="Enable the integration now?")

    print("")
    print("Setup finished.")
    print("You can now use the integration in Z-SOAR!")



if __name__ == "__main__":
    # This integration should not be called directly besides running the integration setup!
    main()