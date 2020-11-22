from provider_actions_class import *


if __name__ == "__main__":
    args = sys.argv


    if len(sys.argv) == 2:
        if args[1] == ("-h" or "--help"):
            print(Fore.YELLOW + "{}".format("actions.py [--update] [update] [localhost] [create] [delete] domainslist.txt"))
            print(Fore.GREEN +"--update          Refreshes the local database for faster queries")
            print(Fore.GREEN +"update            Update domains A record, input must be list with DOMAIN:IP")
            print(Fore.GREEN +"localhost         Set A record to 127.0.0.1 for all domains from list, input must be list with DOMAINS")
            print(Fore.GREEN +"create            Create domains from list and set indicated A record, input must be list with DOMAIN:IP")
            print(Fore.GREEN +"delete            Delete all domains from list, input must be list with DOMAINS")
            sys.exit(1)

    if len(sys.argv) == 2:
        if args[1] == "--update":
            Constellix.update_db()
            sys.exit(1)


    if args[1] == "update":
        all_domains_json = []
        input_domains_list = open(sys.argv[2], 'r').read().splitlines()
        local_db = Constellix.read_local_json()
        if local_db is None:
            all_domains_json = Constellix.update_db()
        else:
            print(Fore.GREEN + "Parsing local JSON")
            all_domains_json = local_db
        print(Fore.GREEN + "Looking for domains identifier...")
        domains_name_and_id = Constellix.looking_for_domain_id(received_json=all_domains_json,
                                                               input_domains=input_domains_list)
        print(Fore.GREEN + "Looking for A record identifier...")
        necessary_domains_data = Constellix.looking_for_domain_A_record_id(domains_name_and_id)
        print(Fore.LIGHTYELLOW_EX + "Missing domains: \n" + str(Constellix.compare(completed=necessary_domains_data,
                                                                                   input=input_domains_list)))
        # Update A record section
        print(Fore.LIGHTMAGENTA_EX + "UPDATE STARTED")
        for domain in necessary_domains_data:
            # list = [ domain_name : domain_id : domain_A_record_id : ip ]
            list = domain.split(":")
            response_code = Constellix.update_record_call(domain_id=list[1], record_id=list[2], IP=list[3])
            print(Fore.GREEN + "{} process status: {} => {}".format(list[0], response_code, list[3]))
        print(Fore.LIGHTCYAN_EX + '\nDone (◣_◢). If domain is WHITE and not found in the current database,', Fore.YELLOW + 'do actions.py --update\n')
        print(Fore.LIGHTCYAN_EX + "Check the \'not_found.txt\' in the script directory to find missing domains.")


    if args[1] == "localhost":
        all_domains_json = []
        domain_and_localhost_ip = []
        input_domains_list = open(sys.argv[2], 'r').read().splitlines()
        for line in input_domains_list:
            domain_and_localhost_ip.append(line.strip()+":127.0.0.1")
        local_db = Constellix.read_local_json()
        if local_db is None:
            all_domains_json = Constellix.update_db()
        else:
            print(Fore.GREEN + "Parsing local JSON")
            all_domains_json = local_db
        print(Fore.GREEN + "Looking for domains identifier...")
        domains_name_and_id = Constellix.looking_for_domain_id(received_json=all_domains_json,
                                                               input_domains=domain_and_localhost_ip)
        print(Fore.GREEN + "Looking for A record identifier...")
        necessary_domains_data = Constellix.looking_for_domain_A_record_id(domains_name_and_id)
        print(Fore.LIGHTYELLOW_EX + "Missing domains: \n" + str(Constellix.compare(completed=necessary_domains_data,
                                                                                   input=domain_and_localhost_ip)))
        # Update A record section
        print(Fore.LIGHTMAGENTA_EX + "UPDATE STARTED")
        for domain in necessary_domains_data:
            # list = [ domain_name : domain_id : domain_A_record_id : ip ]
            list = domain.split(":")
            response_code = Constellix.update_record_call(domain_id=list[1], record_id=list[2], IP=list[3])
            print(Fore.GREEN + "{} process status: {}".format(list[0], response_code))
        print(Fore.LIGHTCYAN_EX + '\nDone (◣_◢). If domain is WHITE and not found in the current database,', Fore.YELLOW + 'do actions.py --update\n')
        print(Fore.LIGHTCYAN_EX + "Check the \'not_found.txt\' in the script directory to find missing domains.")


    if args[1] == 'create':
        print(Fore.LIGHTMAGENTA_EX + "CREATING DOMAINS FROM LIST")
        input_domains_to_create = open(sys.argv[2], 'r').read().splitlines()
        for string in input_domains_to_create:
            domains_name_and_ip = string.split(":")
            response_code = Constellix.create_domain(domains_name_and_ip[0])
            print(Fore.GREEN + "DOMAIN CREATE STATUS: {}".format(response_code))
            try:
                Constellix.create_record(rtype='A', content=domains_name_and_ip[1], domain_id=response_code[0]['id'])
                print(Fore.GREEN + "RECORD CREATED")
            except:
                domain_id_from_error = re.findall(r'\d{5,}', str(response_code['errors']))
                parsed_id = str(domain_id_from_error).replace('\'', '').replace('[', '').replace(']', '')
                temp_ = Constellix.create_record(rtype='A', content=domains_name_and_ip[1], domain_id=int(parsed_id))
                print(Fore.GREEN + "RECORD CREATE STATUS: {}".format(temp_))
        print(Fore.YELLOW + "CONSTELLIX NS:\nns11.constellix.com\nns21.constellix.com\nns31.constellix.com\nns41.constellix.net\nns51.constellix.net\nns61.constellix.net")
        print(Fore.LIGHTCYAN_EX + "Updating local DB after changes")
        Constellix.update_db()

    if args[1] == 'delete':
        input_domains_to_delete = open(sys.argv[2], 'r').read().splitlines()
        all_domains_json = []
        local_db = Constellix.read_local_json()
        if local_db is None:
            all_domains_json = Constellix.update_db()
        else:
            all_domains_json = local_db
        print(Fore.LIGHTMAGENTA_EX + "DELETE STARTED!")
        for input_domain_name in input_domains_to_delete:
            domain_to_delete = input_domain_name.split(":")
            for stored_domain in all_domains_json:
                if domain_to_delete[0] == stored_domain['name']:
                    domain_id = stored_domain['id']
                    response_code = Constellix.delete_domain(domain_id)
                    print(Fore.GREEN + "{}".format(response_code))


    ###if args[1] == ''