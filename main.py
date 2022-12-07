import boto3
import paramiko
import time
import sys
import os

menu = 0

while (menu != '99'):
    print("------------------------------------------------------------")
    print("           Amazon AWS Control Panel using SDK               ")
    print("------------------------------------------------------------")
    print("  1. list instance                2. available zones        ")
    print("  3. start instance               4. available regions      ")
    print("  5. stop instance                6. create instance        ")
    print("  7. reboot instance              8. list images            ")
    print("  9. condor_state                99. quit                   ")
    print("------------------------------------------------------------")

    menu = input("Enter an integer: ")

    # 1. list instance
    if (menu == '1'):
        ec2 = boto3.resource('ec2')
        instance_iterator = ec2.instances.filter(
            Filters=[{'Name': 'tag-key', 'Values': ['Name']}])

        for instance in instance_iterator:
            for tag in instance.tags:
                if tag['Key'] == 'Name':
                    print('[id]'+instance.id+'\t',
                          '[type]'+instance.instance_type+'\t',
                          '[AMI]'+instance.image_id+'\t',
                          '[monitoring state]' +
                          instance.monitoring.get("State")+'\t',
                          '[state]'+instance.state.get("Name")+'\t',
                          '[name]'+tag['Value'])

    # 2. available zones
    elif (menu == '2'):
        ec2 = boto3.client('ec2')

        response = ec2.describe_availability_zones()
        count = 0
        for i in response["AvailabilityZones"]:
            print('[id]'+i['ZoneId']+'\t',
                  '[region]'+i['RegionName']+'\t',
                  '[zone]'+i['ZoneName'])
            count = count + 1
        print('You have access to {} Availability Zones' .format(count))

    # 3. start instance
    elif (menu == '3'):
        ec2 = boto3.client('ec2')

        instanceid = input("Enter instance id: ")

        try:
            ec2.start_instances(
                InstanceIds=[instance_id,],
            )
        except:
            print("Exception")
        else:
            print("Successfully start instance {}".format(instance_id))

    # 4. available regions
    elif (menu == '4'):
        ec2 = boto3.client('ec2')

        response = ec2.describe_regions()

        for i in response["Regions"]:
            print('[region]'+i['RegionName']+'\t'+'[endpoint]'+i['Endpoint'])

    # 5. stop instance
    elif (menu == '5'):
        ec2 = boto3.client('ec2')

        instanceid = input("Enter instance id: ")

        try:
            ec2.stop_instances(
                InstanceIds=[instance_id,],
            )
        except:
            print("Exception")
        else:
            print("Successfully stop instance {}".format(instance_id))

    # 6. create instance
    elif (menu == '6'):
        ec2 = boto3.resource('ec2')

        ami_id = input("Enter ami id: ")

        try:
            ec2.create_instances(
                ImageId=ami_id,
                InstanceType='t2.micro',
                MinCount=1,
                MaxCount=1,
                KeyName='home',
                SecurityGroups=['launch-wizard-8']
            )
        except:
            print("Exception")
        else:
            print("Successfully create instance {}".format(instance_id))

    # 7. reboot instance
    elif (menu == '7'):
        ec2 = boto3.client('ec2')

        instance_id = input("Enter instance id: ")

        try:
            ec2.reboot_instances(
                InstanceIds=[instance_id,],
            )
        except:
            print("Exception")
        else:
            print("Successfully rebooted instance {}".format(instance_id))

    # 8. list images
    elif (menu == '8'):
        ec2 = boto3.client('ec2')

        response = ec2.describe_images(Owners=['self'])

        for i in response["Images"]:
            print('[IamgeID]'+i['ImageId']+'\t'
                  '[Name]'+i['Name']+'\t'
                  '[Owner]'+i['OwnerId'])

    # 9. condor_status
    elif (menu == '9'):
        sys.stdout.flush()
        # ssh_connect

        def ssh_connect_with_retry(ssh, ip_address, retries):
            if retries > 3:
                return False
            privkey = paramiko.RSAKey.from_private_key_file(
                './home.pem')
            interval = 5
            try:
                retries += 1
                ssh.connect(hostname=ip_address,
                            username='ec2-user', pkey=privkey)
                return True
            except Exception as e:
                print(e)
                time.sleep(interval)
                ssh_connect_with_retry(ssh, ip_address, retries)

        # get instance
        ec2 = boto3.resource('ec2')
        instance = ec2.Instance(id="i-0ec86d354f6e359c0")
        instance.wait_until_running()
        current_instance = list(ec2.instances.filter(
            InstanceIds=["i-0ec86d354f6e359c0"]))
        ip_address = current_instance[0].public_ip_address

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_connect_with_retry(ssh, ip_address, 0)

        commands = "condor_status"
        stdin, stdout, stderr = ssh.exec_command(commands)
        status = stdout.readlines()
        for i in range(len(status)):
            status[i] = status[i].rstrip()
            print(status[i])
        ssh.close()
