import logging
import azure.functions as func
import paramiko
import os


def run_script_on_vm():
    host = os.environ.get('VM_IP_ADDRESS')
    port = 22
    username = os.environ.get('VM_USERNAME')
    password = os.environ.get('VM_PASSWORD')
    script_path = '/home/gauk/test/myscript.sh'

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(hostname=host, port=port,
                           username=username, password=password)
        stdin, stdout, stderr = ssh_client.exec_command(f'bash {script_path}')
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read().decode() if exit_status == 0 else stderr.read().decode()
        logging.info(f'Script output: {output}')
        return exit_status, output
    except Exception as e:
        logging.error(f'Error executing the script: {str(e)}')
        return -1, str(e)
    finally:
        ssh_client.close()


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        exit_status, output = run_script_on_vm()
        if exit_status == 0:
            return func.HttpResponse(f"Script executed successfully. Output: {output}", status_code=200)
        else:
            return func.HttpResponse(f"Script execution failed. Error: {output}", status_code=500)
