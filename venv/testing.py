#!/usr/bin/env python

import argparse
import glob
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import uuid
from operator import itemgetter
from random import *
from subprocess import Popen, PIPE
from subprocess import check_output
from xml.dom import minidom

import netaddr
import requests
import serial
from clint.textui import progress
from pybrctl import BridgeController

import tlvinfo
from defxml import CreateXML, CreatePreseed

try:
    import libvirt

    libvirt.VIR_STORAGE_VOL_CREATE_PREALLOC_METADATA = 1
except ImportError:
    print('***\tlibvirt is unavailable\t***\n')
    sys.exit(1)


# https://stackoverflow.com/a/45543887
# Avoiding console prints by Libvirt Qemu python APIs
def libvirt_callback(userdata, err):
    pass


def is_valid_ip(ip):
    return netaddr.valid_ipv4(ip)


def exit_with_error(error='Some error occurred'):
    print(error)
    sys.exit(1)


def input_handler(input_txt, allow_empty=None, default=None, allowed_items=[], input_type='text'):
    retries = 3
    try:
        for _ in range(retries):
            var = raw_input('\n{}'.format(input_txt)).lower().strip()
            if not var and not allow_empty:
                if default:
                    print('No input, default to {}'.format(default))
                    return default
                print('Empty string is not allowed. Please retry')
                continue
            # Return the input as is
            if input_type == 'text' and allowed_items == []:
                return var
            # Return if input matches allowed items
            if allowed_items:
                if var in allowed_items:
                    return var
                else:
                    print('"{}" does not match. Allowed items are: {}. Please retry'.format(var, allowed_items))
                    continue
            # Return if an IP is valid
            if input_type == 'ipv4' and is_valid_ip(var):
                return var
            else:
                print('"{}" is not a valid IPv4 address. Please retry'.format(var))
                continue
        exit_with_error('Invalid parameter, exiting')
    except KeyboardInterrupt:
        exit_with_error('\nInterrupted by user')


def get_board_type():
    try:
        with open('/sys/devices/virtual/dmi/id/product_name', 'r') as f:
            return f.read().replace(' ', '_').replace('(', '').replace(')', '').strip()
    except:
        return "None"


def get_numa_pcidev(numa, nopci, return_all=False):
    if nopci:
        return None

    def read_file(name):
        if os.path.isfile(name):
            with open(name, 'r') as f:
                return f.read().strip()

    results = []  # '0': [], '1': []}
    pci_slots = sorted(glob.glob("/sys/bus/pci/slots/*"))
    # ['/sys/bus/pci/slots/1', '/sys/bus/pci/slots/2, ...]
    for pci_id in pci_slots:
        addr = read_file('{}/address'.format(pci_id))
        # addr - '0000:08:00'
        numa_id = read_file('/sys/bus/pci/devices/{}.1/numa_node'.format(addr))
        if numa_id is not None and int(numa_id) == int(numa):
            lspci_cmd = 'lspci -s {}'.format(addr)  # | grep -i "Ethernet controller: Mellanox"'
            process = Popen(lspci_cmd.split(' '), stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            interfaces = ['Mellanox', 'Intel']
            for int_type in interfaces:
                results += [line.split()[0] for line in stdout.split('\n') if int_type in line]

    if return_all is True:
        return results

    try:
        if "ProLiant_DL380_Gen10" in get_board_type():
            return "{}|07:00.0,{}|08:00.0".format(results[1], results[3])
        else:
            return "{}|07:00.0,{}|08:00.0".format(results[0], results[1])
    except:
        return None


def get_available_numas():
    path = '/sys/devices/system/node/node'
    return [node_id.replace(path, '') for node_id in glob.glob('{}*'.format(path)) if node_id]


def get_cpu_for_re(cores):
    cpu_map_by_numa = dict()
    ls_cpu = check_output(["lscpu", "-p=Node,CPU"])
    # The following is the parsable format, which can be fed to other
    # programs. Each different item in every column has an unique ID
    # starting from zero.
    # Node,CPU

    for item in ls_cpu.split('\n'):
        if item and not item.startswith('#'):
            node, cpu = item.split(',')
            if node not in cpu_map_by_numa:
                cpu_map_by_numa[node] = list()
            cpu_map_by_numa[node].append(cpu)

    ret_list = []

    # Set a default number of cores if wasn't provided by argument
    cores_per_vm = 8 if cores is None else cores
    for key, value in sorted(cpu_map_by_numa.items(), key=itemgetter(1)):
        for i in xrange(2, len(value), cores_per_vm):
            tmp_list = value[i:i + cores_per_vm]  # ['16', '17', '27', '28', '29']
            if len(tmp_list) == cores_per_vm:
                results = [[tmp_list[0]]]
                for num in tmp_list[1:]:
                    if int(results[-1][-1]) + 1 != int(num):
                        results.append([])
                    results[-1].append(num)

                cpu = []
                for item in results:
                    if len(item) > 1:
                        cpu.append('{}-{}'.format(item[0], item[-1]))
                    else:
                        cpu.append(item[0])
                    cpu.append(',')
                cpu_list = (key, ''.join(cpu[:-1]))
                ret_list.append(cpu_list)
    return ret_list


def return_cpu_by_numa(numa, cpu_shift=2):
    cpumap = '/sys/devices/system/node/node{}/cpulist'.format(numa)
    try:
        with open(cpumap, 'r') as f:
            cpus = f.read()
        tmp_list = cpus.strip().split('-')
        tmp_list[0] = str(int(tmp_list[0]) + cpu_shift)
        return '-'.join(tmp_list)
    except Exception as err:
        print(err)
    return 'ERROR'


def get_host_free_memory():
    """

    Returns:
         int: Amount of a free memory in Gb
    """
    return int(os.popen("free -g | grep Mem").readlines()[0].split()[3])


def hugepages(memory):
    less_then_total = 25
    amount = int(memory) - less_then_total
    if amount < 10:
        amount = 10
    return amount


def get_free_disk_space():
    """
    Returns:
        int: Number of free space in GB
    """
    virsh_partition = '/var/lib/libvirt/images'
    stat = os.statvfs(virsh_partition)
    return stat.f_bfree * stat.f_bsize / 1024 / 1024 / 1024


def get_free_hugepages_per_numa(numa_id, requested):
    """
    Args:
        numa_id (str): Numa's ID
        requested (int): Requested amount of hugepages in GB
    Returns:
        int: Amount of requested or free hugepages in GB, Error if no hugepages found
    """
    try:
        filename = "/sys/devices/system/node/node{}/hugepages/hugepages-1048576kB/free_hugepages".format(numa_id)
        with open(filename, 'r') as f:
            max_available = int(f.read().strip())
        return requested if max_available > requested else max_available
    except Exception as err:
        print(err)
        print("Cant find any 1GB hugepages")
        sys.exit(1)


def host_types(no_pci, cores, memory, memory_is_hugepage, disk, is_dev_vm):
    dnor_memory = 64 if memory is None else memory
    re_memory = 32 if memory is None else memory
    fe_memory = 75 if memory is None else memory
    mgmt_memory = re_memory
    re_disk_gb = 185 if disk is None else disk
    fe_disk_gb = 128 if disk is None else disk
    mgmt_disk_gb = fe_disk_gb
    dnor_disk_gb = fe_disk_gb
    re_prefix = 're'

    # Overwrite hardware settings when createing a dev VM
    if is_dev_vm:
        re_prefix = 'dev'
        re_disk_gb = 90
        re_memory = 32
        memory_is_hugepage = True
        cores = 6

    cpu_list = get_cpu_for_re(cores)
    host_type = dict(mgmt0=dict(cpu=cpu_list[0][1], memory=mgmt_memory, disk_size_GB=mgmt_disk_gb, hugepages=False),
                     mgmt1=dict(cpu=cpu_list[1][1], memory=mgmt_memory, disk_size_GB=mgmt_disk_gb, hugepages=False),
                     dnor=dict(cpu=cpu_list[0][1], memory=dnor_memory, disk_size_GB=dnor_disk_gb, hugepages=False))

    overall_available_hugepages = 0
    for numa_id in get_available_numas():
        available_hugepages = get_free_hugepages_per_numa(numa_id, fe_memory)
        overall_available_hugepages += available_hugepages
        pcidev = get_numa_pcidev(numa_id, no_pci)
        if pcidev or no_pci:
            host_type["fe{}".format(numa_id)] = dict(cpu=return_cpu_by_numa(numa_id),
                                                     pcidev=pcidev,
                                                     memory=available_hugepages,
                                                     memory_recommended=fe_memory,
                                                     disk_size_GB=fe_disk_gb,
                                                     hugepages=True,
                                                     hugepages_amount=hugepages(available_hugepages),
                                                     numa=int(numa_id))
        else:
            print("*** No pci devices found for FE, cant select type FE ***")

    free_memory = get_host_free_memory()
    if memory_is_hugepage:
        memory_to_allocate = re_memory if re_memory <= overall_available_hugepages else overall_available_hugepages
    else:
        memory_to_allocate = re_memory if re_memory <= free_memory else free_memory
    for item in range(len(cpu_list)):
        host_type["{}{}".format(re_prefix, item)] = dict(cpu=cpu_list[item][1],
                                                         memory=memory_to_allocate,
                                                         memory_recommended=re_memory,
                                                         disk_size_GB=re_disk_gb,
                                                         hugepages=memory_is_hugepage)
    return host_type


def warn_if_hyper_threading_is_enabled():
    tpl = check_output(["lscpu"])
    threads = ''.join([l for l in tpl.split('\n') if 'Thread(s) per core' in l])
    if threads and threads.split()[-1] != '1':
        print('\n***\tWarning: A hyper threading is enabled - {}\t***'.format(threads))


class VirtLibTools:
    def __init__(self):
        # # https://stackoverflow.com/a/45543887
        libvirt.registerErrorHandler(f=libvirt_callback, ctx=None)
        self.connection = libvirt.open("qemu:///system")
        self.pool = 'default'
        self.images_location = '/var/lib/libvirt/images'

    def __del__(self):
        self.connection.close()

    def get_vir_dom_object_by_name(self, domain):
        try:
            return self.connection.lookupByName(domain)
        except:
            return None

    def create_storage(self, name, capacity):
        vol_xml = """
        <volume>
          <name>{name}.img</name>
          <allocation>0</allocation>
          <capacity unit="G">{capacity}</capacity>
          <target>
            <path>{path}/{name}.img</path>
            <format type='qcow2'/>
            <permissions>
              <owner>107</owner>
              <group>107</group>
              <mode>0744</mode>
              <label>virt_image_t</label>
            </permissions>
          </target>
        </volume>""".format(name=name, path=self.images_location, capacity=capacity)
        pool = self.connection.storagePoolLookupByName(self.pool)
        pool.createXML(vol_xml, flags=1)

    def remove_domain(self, domain):
        try:
            dom = self.connection.lookupByName(domain)
            dom.undefine()
        except Exception as err:
            print(err)

    def remove_volume(self, volume):
        try:
            default_pool = self.connection.storagePoolLookupByName(self.pool)
            vol = default_pool.storageVolLookupByName(volume)
            vol.delete()
        except Exception as err:
            print(err)

    def is_domain_running(self, domain):
        try:
            dom = self.connection.lookupByName(domain)
            return dom.isActive() == 1
        except libvirt.libvirtError:
            return False

    def is_domain_exists(self, domain):
        try:
            self.connection.lookupByName(domain)
            return True
        except libvirt.libvirtError:
            return False

    def is_volume_exists(self, image):
        default_pool = self.connection.storagePoolLookupByName(self.pool)
        volumes_list = default_pool.listVolumes()
        return '{}.img'.format(image) in volumes_list

    def define_xml(self, xml):
        """
        Args:
            xml (str): Guest VM configuration in XML format
        Returns:
            libvirt.virDomain: libvirt.virDomain object or None in case of Error
        """
        return self.connection.defineXML(xml)

    def start_domain(self, dom):
        """
        Args:
            dom (libvirt.virDomain): libvirt.virDomain object of domain to be started
        Returns:
            bool: True upon successful domain start, False otherwise
        """
        try:
            return dom.create() == 0
        except:
            return -1

    def console(self, domain):
        dom = self.connection.lookupByName(domain)
        raw_xml = dom.XMLDesc(0)
        xml = minidom.parseString(raw_xml)
        domain_types = xml.getElementsByTagName('console')
        device = domain_types[0].getAttribute('tty')
        print('\nStarting console...')
        print("Escape character is ^C")
        print('.......................\n\n')
        with serial.Serial(device, timeout=1) as ser:
            print('Reading from {}'.format(ser.name))
            while True:
                try:
                    output = ser.readline()
                    if output:
                        print(output.strip())
                except:
                    break


class DefineAndStartVM(object):
    def __init__(self, vm_type, vm_name, tmp_dir, debug, uefi, onie, jenkins_node):
        self.vm_type = vm_type
        self.vm_name = vm_name
        self.tmp_dir = tmp_dir
        self.debug = debug
        self.uefi = uefi
        self.onie = onie
        self.jenkins_node = jenkins_node
        self.virsh = VirtLibTools()

    def run_cmd(self, command):
        process = Popen(command.split(), stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        return stdout, stderr

    def download_file(self, url, save_as, proxy=None):
        if proxy:
            proxy = {"http": proxy}
        r = requests.get(url, stream=True, proxies=proxy)
        with open(save_as, 'wb') as f:
            total_length = int(r.headers.get('content-length'))
            for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
                if chunk:
                    f.write(chunk)
                    f.flush()

    def create_vm(self, boot_dir, random_num, location, customers, dist, vm_properties, atomic):
        try:
            if self.jenkins_node:
                self.download_file("http://kvm10.dev.drivenets.net/onie-recovery-x86_64-kvm_x86_64-r0.jenkins.iso",
                                   "{}/onie-recovery.iso".format(boot_dir),
                                   customers[dist].get('proxy'))
            elif self.onie:
                self.download_file("http://kvm10.dev.drivenets.net/onie-recovery-x86_64-kvm_x86_64-r0.vda.iso",
                                   "{}/onie-recovery.iso".format(boot_dir),
                                   customers[dist].get('proxy'))
            else:
                self.download_file("{}/initrd.gz".format(location),
                                   "{}/virtinst-initrd.gz-{}".format(boot_dir, random_num),
                                   customers[dist].get('proxy'))
                self.download_file("{}/linux".format(location),
                                   "{}/virtinst-linux-{}".format(boot_dir, random_num),
                                   customers[dist].get('proxy'))

                custom_apt_keys_file = '{}/repo_keys'.format(boot_dir)
                if os.path.exists(custom_apt_keys_file):
                    os.remove(custom_apt_keys_file)

                with open(custom_apt_keys_file, 'w') as fw:
                    for apt_key in customers[dist].get('keys', {}).values():
                        fw.write('{}\n'.format(apt_key))
                self.inject_initrd(custom_apt_keys_file,
                                   '{}/virtinst-initrd.gz-{}'.format(boot_dir, random_num))

                custom_apt_urls_file = '{}/repo_urls'.format(boot_dir)
                if os.path.exists(custom_apt_urls_file):
                    os.remove(custom_apt_urls_file)

                with open(custom_apt_urls_file, 'w') as fw:
                    for repo in customers[dist].get('repo', {}).values():
                        fw.write('{}\n'.format(repo))
                self.inject_initrd(custom_apt_urls_file,
                                   '{}/virtinst-initrd.gz-{}'.format(boot_dir, random_num))

                preseed_cfg_location = '{}/preseed.cfg'.format(self.tmp_dir)
                CreatePreseed().build_preseed_file(preseed_cfg_location, self.vm_type, customers, dist, vm_properties,
                                                   atomic,
                                                   self.debug, self.uefi)

                self.inject_initrd(preseed_cfg_location,
                                   '{}/virtinst-initrd.gz-{}'.format(boot_dir, random_num))
                self.inject_initrd('/opt/drivenets/libvirt/guest-bootstrap.sh',
                                   '{}/virtinst-initrd.gz-{}'.format(boot_dir, random_num))

        except Exception as err:
            print(err)
            sys.exit(1)

        step1 = '{}/{}-step1.xml'.format(self.tmp_dir, self.vm_type)
        with open(step1, 'r') as f:
            xml = f.read()
        dom = self.virsh.define_xml(xml)
        if dom is None:
            exit_with_error(error="Failed to define domain from {}".format(step1))

        if self.virsh.start_domain(dom) is False:
            exit_with_error(error="Can not boot guest domain.")

    def update_vm(self):
        step2 = '{}/{}-step2.xml'.format(self.tmp_dir, self.vm_type)
        with open(step2, 'r') as f:
            xml = f.read()
        dom = self.virsh.define_xml(xml)
        dom.setAutostart(1)
        print("To view the console, run:\nvirsh console {}".format(self.vm_name))

    def inject_initrd(self, filename, initrd):
        scratch_dir = '/tmp/'
        tempdir = tempfile.mkdtemp(dir=scratch_dir)
        shutil.copy(filename, tempdir)
        find_proc = subprocess.Popen(['find', '.', '-print0'],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     cwd=tempdir)
        cpio_proc = subprocess.Popen(['cpio', '-o', '--null', '-Hnewc', '--quiet'],
                                     stdin=find_proc.stdout,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     cwd=tempdir)
        f = open(initrd, 'ab')
        gzip_proc = subprocess.Popen(['gzip'], stdin=cpio_proc.stdout, stdout=f, stderr=subprocess.PIPE)
        cpio_proc.wait()
        find_proc.wait()
        gzip_proc.wait()
        f.close()
        shutil.rmtree(tempdir)


def main():
    if os.getuid() == 0:
        boot_dir = '/var/lib/libvirt/boot'
    else:
        boot_dir = os.environ['HOME']

    def get_bridge_names():
        brctl = BridgeController()
        return [x.name for x in brctl.showall()]

    dn_password = "$6$JNimi4bR$u/jLM53caWf/dvXVEbBeC8NHIq3D3py3fbgLCncypluWP6BHNp.0G0zLcbjk8z8khpUCDYrfchOmLx8Q359QM."
    dn_proxy = "http://proxy.dev.drivenets.net:3128"
    arch = "amd64"
    customers = {
        "dn": {
            "trusty": {
                "repo": {"repo1": "http://dnrepo.s3-accelerate.amazonaws.com/trusty trusty main"},
                "keys": {"repo1": "http://dnrepo.s3-accelerate.amazonaws.com/Release.key"},
                "mirror": "il.archive.ubuntu.com",
                "installer": "il.archive.ubuntu.com/ubuntu/dists/trusty",
                "proxy": dn_proxy,
                "password": dn_password
            },
            "xenial": {
                "repo": {"repo1": "http://dnrepo.s3-accelerate.amazonaws.com/xenial xenial main"},
                "keys": {"repo1": "http://dnrepo.s3-accelerate.amazonaws.com/Release.key"},
                "mirror": "il.archive.ubuntu.com",
                "installer": "il.archive.ubuntu.com/ubuntu/dists/xenial",
                "proxy": dn_proxy,
                "password": dn_password
            },
            "bionic": {
                "repo": {"repo1": "http://dnrepo.s3-accelerate.amazonaws.com/bionic bionic main",
                         "repo2": "[arch=amd64] http://repo.saltstack.com/apt/ubuntu/18.04/amd64/2018.3 bionic main"},
                "keys": {"repo1": "http://dnrepo.s3-accelerate.amazonaws.com/Release.key",
                         "repo2": "https://repo.saltstack.com/apt/ubuntu/18.04/amd64/2018.3/SALTSTACK-GPG-KEY.pub"},
                "mirror": "il.archive.ubuntu.com",
                "installer": "il.archive.ubuntu.com/ubuntu/dists/bionic",
                "proxy": dn_proxy,
                "password": dn_password
            }
        }
    }
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    warn_if_hyper_threading_is_enabled()
    available_customers = ['dn']
    available_dists = ["trusty", "xenial", "bionic"]
    available_net_items = ['dhcp', 'static']

    node_types = {'tiny': {'disk': 60, 'memory': 8, 'cores': 2},
                  'small': {'disk': 60, 'memory': 12, 'cores': 4},
                  'medium': {'disk': 60, 'memory': 30, 'cores': 6}}

    # Get arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", type=str, help="Guest Type")
    parser.add_argument("--customer", choices=available_customers, type=str, help="Customer (dn)")
    parser.add_argument("--name", type=str, help="Guest Name")
    parser.add_argument("--dist", choices=available_dists, type=str, help="Guest Ubuntu Version")
    parser.add_argument("--bridge", type=str, help="Bridge Interfaces")
    parser.add_argument("--management", type=str, help="DRIVENETS Management server", default='')
    parser.add_argument("--net", choices=available_net_items, type=str, help="Guest Network Type (dhcp/static)")
    parser.add_argument("--ip", type=str, help="(ONLY IF USING STATIC) Guest IP Address")
    parser.add_argument("--subnet", type=str, help="(ONLY IF USING STATIC) Guest Subnet Address")
    parser.add_argument("--gateway", type=str, help="(ONLY IF USING STATIC) Guest Default Gateway")
    parser.add_argument("--dns", type=str, help="(ONLY IF USING STATIC) Guest DNS")
    parser.add_argument("--proxy", type=str, help="Guest proxy. Use '' for no proxy")
    parser.add_argument("--force", action='store_true', help="Removes stopped VM with such a name or an orphan image")
    parser.add_argument("--debug", action='store_true', help="debug install")
    parser.add_argument("--uefi", action='store_true', help="use UEFI rom")
    parser.add_argument("--onie", action='store_true', help="Embed ONIE")
    parser.add_argument("--jenkins", action='store_true', help="jenkins ONIE")
    parser.add_argument("--static_node_type", choices=node_types, type=str, help='Define VM values from template')
    parser.add_argument("--console", action='store_true', help="Start a libvirt console when creating a new Guest VM")
    parser.add_argument("--nopci", action='store_true', help="Install forwarder without PCI devices")
    parser.add_argument("--atomic", action='store_true', help="Install filesystem as one large partition")
    parser.add_argument("--cores", type=int, help="Define Number of vCPU")
    parser.add_argument("--memory", type=int, help="Define VM memory size (in GB)")
    parser.add_argument("--force_hugepages", action='store_true', help="Use HugePages for memory")
    parser.add_argument("--disk", type=int, help='Define VM disk size (in GB)')
    parser.add_argument("--dev", action='store_true', help=argparse.SUPPRESS)

    args = parser.parse_args(sys.argv[1:])

    static_node_type = args.static_node_type

    memory = None
    disk = None
    cores = None

    if static_node_type and node_types.get(static_node_type):
        memory = node_types[static_node_type]['memory']
        disk = node_types[static_node_type]['disk']
        cores = node_types[static_node_type]['cores']

    if args.nopci:
        print("installing FE without PCI, need to manually add them later")

    cores = args.cores if args.cores else cores
    memory = args.memory if args.memory else memory
    disk = args.disk if args.disk else disk

    onie = args.onie
    uefi = args.uefi
    jenkins_node = args.jenkins
    memory_is_hugepage = args.force_hugepages

    if static_node_type:
        jenkins_node = True

    if jenkins_node:
        onie = True

    if onie:
        uefi = True
        memory_is_hugepage = True

    uefi_rom = '/usr/share/ovmf/OVMF.fd'
    if not os.path.exists(uefi_rom):
        exit_with_error('cant find UEFI ROM {}'.format(uefi_rom))

    is_dev_vm = args.dev
    # set Atomic = True if defined or if dev_vvm
    atomic = True if is_dev_vm else args.atomic

    min_vm_memory = 16 if memory is None else memory
    available_guest_types = host_types(args.nopci, cores, memory, memory_is_hugepage, disk, is_dev_vm)

    # Select a VM type
    print('\nAvailable host types:')
    for available_vm_type in sorted(available_guest_types.iteritems()):
        print('{} - {}'.format(available_vm_type[0], ['{}: {}'.format(item[0], item[1]).replace('_', ' ')
                                                      for item in sorted(available_vm_type[1].iteritems())]))

    vm_type = args.type
    msg = "\nVM Type: "
    if vm_type in available_guest_types.keys():
        print("{}{}".format(msg, vm_type))
    else:
        vm_type = input_handler(msg, allowed_items=available_guest_types.keys())

    vm_properties = available_guest_types.get(vm_type, {})
    if not args.nopci and vm_type.startswith('re'):
        pci_devs = list()
        for numa_id in get_available_numas():
            pci_devs += get_numa_pcidev(numa_id, args.nopci, return_all=True)

        # pci_devs_
        pci_dev_default = 'nopci'
        msg = "\nPCI devices. Up to 2 devices allowed ({}, default is {}): ".format(",".join(pci_devs), pci_dev_default)
        pci_dev = input_handler(msg, default=pci_dev_default)
        if len(pci_dev.split(',')) > 2:
            exit_with_error('Too many PCI cards are selected: {}'.format(pci_dev))

        if pci_dev != 'nopci':
            vm_properties['pcidev'] = pci_dev

    vm_memory = available_guest_types[vm_type]['memory']
    vm_memory_recommended = available_guest_types[vm_type].get('memory_recommended')
    if vm_memory < min_vm_memory:
        exit_with_error(error="Not enough memory for selected vm type, have {}GB, "
                              "at least {}GB is required".format(vm_memory, min_vm_memory))
    elif vm_memory < vm_memory_recommended:
        print("Warning, can only allocate {}GB memory, "
              "recommended amount is {}GB".format(vm_memory, vm_memory_recommended))

    min_vm_disk_size = 10
    host_free_disk_size = get_free_disk_space()
    if host_free_disk_size < min_vm_disk_size:
        exit_with_error(error="Not enough free disk space for selected VM type, have {}GB, "
                              "at least {}GB is required".format(host_free_disk_size, min_vm_disk_size))

    # Select a customer type
    customer = args.customer
    customer_default = 'dn'
    if onie:
        customer = customer_default
    else:
        msg = "\nCustomer (dn, default is {}): ".format(customer_default)
        if customer in available_customers:
            print("{}{}".format(msg, customer))
        else:
            customer = input_handler(msg, allowed_items=available_customers, default=customer_default)

    server_name = str(socket.gethostname())

    # Input a VM name
    vm_name = args.name
    msg = "\nGuest Name: "
    if vm_name:
        print("{}{}create_xml".format(msg, vm_name))
    else:
        vm_name = input_handler(msg)

    if customer == "dn":
        vm_name = '{}-{}'.format(server_name, vm_name)

    debug = args.debug
    virsh = VirtLibTools()
    force_remove_stopped_vm = args.force
    if virsh.is_domain_exists(vm_name):
        if not force_remove_stopped_vm:
            exit_with_error('Domain {} already exists\n'.format(vm_name))
        if virsh.is_domain_running(vm_name):
            exit_with_error('Domain {} already exists and running, can not be removed\n'.format(vm_name))
        print('* Removing domain {}'.format(vm_name))
        virsh.remove_domain(vm_name)

    if virsh.is_volume_exists(vm_name):
        if not force_remove_stopped_vm:
            msg = '\nVolume {0}.img already exists\n' \
                  'To delete, run \n' \
                  'virsh vol-delete --pool=default {0}.img\n' \
                  'virsh undefine --remove-all-storage {0}\n'.format(vm_name)
            exit_with_error(msg)
        print('* Removing volume {}.img'.format(vm_name))
        virsh.remove_volume('{}.img'.format(vm_name))

    # Select a VM dist
    dist = 'bionic'
    if not onie:
        dist_default = 'bionic'  # if is_dev_vm or "Gen10" in get_board_type() or vm_type == 'dnor' else 'trusty'
        dist = args.dist
        msg = "\nUbuntu dist (trusty [14.04] / xenial [16.04] / bionic [18.04], default is {}): ".format(dist_default)
        if dist:
            print('{}{}'.format(msg, dist))
        else:
            dist = input_handler(msg, allowed_items=available_dists, default=dist_default)

    # Select a bridge interface
    bridge_args = get_bridge_names()
    bridge_interface = args.bridge.split(',') if args.bridge else None
    msg = "\nBridge interfaces (available bridges: {}, default is {}): ".format(",".join(bridge_args), bridge_args[0])
    if bridge_interface and not list(set(bridge_interface).difference(bridge_args)):
        print("{}{}".format(msg, bridge_interface))
    else:
        bridge_interface = input_handler(msg, default=bridge_args[0]).split(',')

    # Select a network type
    net_config = args.net
    net_config_default = 'dhcp'
    if onie:
        net_config = net_config_default
    else:
        msg = "\nNetwork type (dhcp / static, default is {}): ".format(net_config_default)
        if net_config in available_net_items:
            print("{}{}".format(msg, net_config))
        else:
            net_config = input_handler(msg, allowed_items=available_net_items, default=net_config_default)

    # Management server configuration
    if vm_type.startswith('dev') or vm_type in ['mgmt0', 'mgmt1', 'dnor']:
        mgmt_addr = 'None'
    else:
        mgmt_addr = args.management
        mgmt_addr_default = "salt" if jenkins_node else "vpesalt"
        msg = "\nDRIVENETS Management server: "
        if mgmt_addr:
            print("{}{}".format(msg, mgmt_addr))
        else:
            mgmt_addr = input_handler(msg, default=mgmt_addr_default)

    # Configure network
    if net_config == "static":
        guest_ip = args.ip
        msg = "\nGuest IP: "
        if guest_ip and is_valid_ip(guest_ip):
            print("{} {}".format(msg, guest_ip))
        else:
            guest_ip = input_handler(msg, input_type='ipv4')

        guest_subnet = args.subnet
        msg = "\nSubnet: "
        if guest_subnet and is_valid_ip(guest_subnet):
            print("{} {}".format(msg, guest_subnet))
        else:
            guest_subnet = input_handler(msg, input_type='ipv4')

        guest_gw = args.gateway
        msg = "\nDefault gw: "
        if guest_gw and is_valid_ip(guest_gw):
            print("{} {}".format(msg, guest_gw))
        else:
            guest_gw = input_handler(msg, input_type='ipv4')

        guest_dns = args.dns
        msg = "\nDNS Server: "
        if guest_dns and is_valid_ip(guest_dns):
            print("{} {}".format(msg, guest_dns))
        else:
            guest_dns = input_handler(msg, input_type='ipv4')

        network_settings = {"guest_ip": guest_ip, "guest_subnet": guest_subnet, "guest_gw": guest_gw,
                            "guest_dns": guest_dns, "guest_proxy": customers[customer][dist].get('proxy', '')}
    else:
        network_settings = {"guest_proxy": customers[customer][dist].get('proxy', '')}

    full_url = "http://{}/main/installer-amd64/current/images/netboot/ubuntu-installer/{}/".format(
        customers[customer][dist]['installer'], arch)

    # print(full_url)

    random_uuid = str(uuid.uuid4())
    random_num = randint(1, 10000)
    tmp_dir = tempfile.mkdtemp()

    virsh.create_storage(vm_name, available_guest_types[vm_type]["disk_size_GB"])

    if onie:
        tlvinfo.generate_tlv(vm_name, mgmt_addr)

    print('Creating Volume')
    guest_vm = DefineAndStartVM(vm_type, vm_name, tmp_dir, debug, uefi, onie, jenkins_node)
    xml = CreateXML(vm_type, vm_name, vm_memory, random_uuid, tmp_dir, available_guest_types, uefi, onie)

    xml.create_xml(boot_dir, random_num, bridge_interface, network_settings, mgmt_addr)
    guest_vm.create_vm(boot_dir, random_num, full_url, customers[customer], dist, vm_properties, atomic)

    xml.update_xml(bridge_interface)
    guest_vm.update_vm()

    print('Removing temporary dir - {}'.format(tmp_dir))
    if not debug:
        shutil.rmtree(tmp_dir)

    # Start a libvirt console if required by args
    if args.console or debug:
        if os.getenv("SUDO_USER") is None:
            print("\n* Can not access serial port. Root permissions are required.")
            print("* Installation is running in background.")
            print("* To view the console manually, run:\nvirsh console {}\n".format(vm_name))
            return
        virsh.console(vm_name)
        if not virsh.is_domain_running(vm_name):
            dom = virsh.get_vir_dom_object_by_name(vm_name)
            print(virsh.start_domain(dom))


if __name__ == '__main__':
    main()