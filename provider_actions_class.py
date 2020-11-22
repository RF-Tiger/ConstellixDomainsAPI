import hashlib, hmac, base64, time, requests, os, sys, json, datetime, re
from colorama import Fore, init

now_time = datetime.datetime.now()
snapshot_time = now_time.strftime("%d-%m-%Y-%H-%M")
init()

##CONST
_API_ENDPOINT: str = "https://api.dns.constellix.com/"
_API_KEY = ""
_API_SECRET_KEY = ""
_GET_ALL_DOMAINS_LINK: str = "v1/domains?offset=0&sort=name&order=asc"
_TTL: int = 180


class Constellix():


    @classmethod
    def return_local_DB_path(cls):
        current_script_directory: str = str(os.getcwd())
        files = os.listdir(current_script_directory)
        local_json = list(filter(lambda x: x.endswith('.json'), files))
        try:
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), local_json[0])
            return path
        except:
            print(Fore.LIGHTYELLOW_EX + "Local DB is missing, can't add changes to local storage. Please use --update")

    @classmethod
    def read_local_json(cls):
        path = []
        current_script_directory: str = str(os.getcwd())
        files = os.listdir(current_script_directory)
        local_json = list(filter(lambda x: x.endswith('.json'), files))
        try:
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), local_json[0])
            json_file = open(path, 'r')
            data = json.loads(json_file.read())
            json_file.close()
            return data
        except:
            print(Fore.RED + "Read local json: ERROR")

    @classmethod
    def update_db(cls):
        #Get all .json files from script directory
        current_script_directory = str(os.getcwd())
        files = os.listdir(current_script_directory)
        local_json = list(filter(lambda x: x.endswith('.json'), files))
        try:
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), local_json[0])
            os.remove(path)
            print(Fore.LIGHTGREEN_EX + "OLD   '{}'   DELETED, DOWNLOADING NEW...!".format(local_json[0]))
            all_domains_json = Constellix.REQUEST()
            # Make a json backup to execute queries faster. If domain is white & missing try to update use '--update'
            with open(snapshot_time + '_dump.json', 'w') as outfile:
                json.dump(all_domains_json, outfile)
            print(Fore.GREEN + "UPDATE DONE")
        except:
            print(Fore.LIGHTRED_EX + "<<<<<<<< First execution can be slow >>>>>>>")
            print(Fore.GREEN +"Receive domains data...")
            all_domains_json = Constellix.REQUEST()
            # Make a json backup to execute queries faster. If domain is white & missing try to update use '--update'
            with open(snapshot_time + '_dump.json', 'w') as outfile:
                json.dump(all_domains_json, outfile)
            print(Fore.GREEN + "UPDATE DONE")
        return all_domains_json



    @staticmethod
    def REQUEST(url: object = None, action: object = None, data: object = None,
                query_params: object = None) -> object:

        # When called without a parameter, it returns a json with information about all domains and their data
        if url is None:
            url = "v1/domains?offset=0&sort=name&order=asc"
        if action is None:
            action = "GET"
        if data is None:
            data = {}
        if query_params is None:
            query_params = {}

        default_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'x-cnsdns-apiKey': _API_KEY,
        }
        # Time string in epoch format
        request_time = str(int(time.time() * 1000))

        hashed = hmac.new(_API_SECRET_KEY.encode(
            'utf-8'), request_time.encode('utf-8'), digestmod=hashlib.sha1)

        default_headers['x-cnsdns-requestDate'] = request_time
        default_headers['x-cnsdns-hmac'] = base64.b64encode(hashed.digest())
        response = requests.request(action, _API_ENDPOINT + url,
                                    params=query_params,
                                    data=json.dumps(data),
                                    headers=default_headers, )
        result = json.loads(response.text)
        status_code = response.status_code

        if status_code == 400:
            print(Fore.RED + "Somewhat what you wanna do - already exist!")
        return result

    # Searching domain ID by name to perform future actions
    @staticmethod
    def looking_for_domain_id(received_json, input_domains):
        list_of_domains_id = []
        for domains in input_domains:
            domains_name_and_ip = domains.split(":")
            for domain in received_json:
                if domains_name_and_ip[0] == domain['name']:
                    list_of_domains_id.append("{}:{}:{}".format(domain['id'], domain['name'], domains_name_and_ip[1]))
        return list_of_domains_id

    # This func. return a list with [ domain_name : domain_id : domain_A_record_id : ip ]
    @staticmethod
    def looking_for_domain_A_record_id(domains_name_and_id):
        completed_data = []
        for domains in domains_name_and_id:
            domains_info = domains.split(":")
            # Using domain-ID we search his domain A-record ID
            link = "v1/domains/{}/records/{}/".format(domains_info[0], 'A')
            received_A_record_json = Constellix.REQUEST(url=link, action='GET')
            for A_record_id in received_A_record_json:
                completed_data.append(
                    "{3}:{2}:{1}:{0}".format(domains_info[2], A_record_id['id'], domains_info[0], domains_info[1]))
        return completed_data

    @staticmethod
    def update_record_call(domain_id, record_id, IP, rtype=None):
        if rtype is None:
            rtype = 'A'
        data = {
            'ttl': _TTL}
        data['roundRobin'] = []
        data['roundRobin'].append({'disableFlag': False,
                                   'value': IP})
        return Constellix.REQUEST(url='v1/domains/{0}/records/{1}/{2}/'.format(domain_id, rtype, record_id),
                                  action='PUT',
                                  data=data)

    @staticmethod
    def create_domain(name):
        data = {"names": [name]}
        return Constellix.REQUEST(url='v1/domains', action='POST', data=data)


    @staticmethod
    def create_record(rtype, content, domain_id):
        if rtype is None:
            rtype = 'A'
        record = {
            "recordType": "a",
            "ttl": _TTL,
            "roundRobin": [
                {
                    "disableFlag": False,
                    "value": content
                }
            ]
        }
        payload = Constellix.REQUEST(url="v1/domains/{0}/records/{1}/".format(domain_id, rtype), action="POST", data=record)
        return payload


    @staticmethod
    def delete_domain(domain_id):
        return Constellix.REQUEST(url="v1/domains/{}".format(domain_id), action='DELETE')

    @staticmethod
    def compare(completed, input):
        comp1 = []
        comp2 = []
        for domain_ in input:
            domains_name = domain_.split(":")
            comp1.append(domains_name[0])
        for domain_2 in completed:
            domain_name_2 = domain_2.split(":")
            comp2.append(domain_name_2[0])
        result = (set(comp1) ^ set(comp2))
        f = open('not_found.txt', 'w')
        for file in result:
            f.write("%s\n" % file)
        f.close()
        return result
