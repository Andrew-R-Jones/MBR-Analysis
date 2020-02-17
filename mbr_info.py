#!/usr/bin/python3

import sys
import hashlib
import os

# empty lists to hold bytes taken from raw image
boot_strap = []
part_1 = []
part_2 = []
part_3 = []
part_4 = []
boot_rcd_sig = []

# dictionary to hold all partition types, key = hex code, value = type
partitions_types_dict = {
    "00": "Empty",
    "01": "FAT12",
    "02": "XENIX root",
    "03": "XENIX usr",
    "04": "FAT16 <32M",
    "05": "Extended",
    "06": "FAT16",
    "07": "IFS; HPFS; NTFS; exFAT; QNX",
    "08": "AIX",
    "09": "AIX bootable",
    "0a": "OS/2 Boot Manag",
    "0b": "W95 FAT32",
    "0c": "W95 FAT32 (LBA)",
    "0e": "W95 FAT16 (LBA)",
    "0f": "W95 Ext'd (LBA)",
    "10": "OPUS",
    "11": "Hidden FAT12",
    "12": "Compaq diagnost",
    "14": "Hidden FAT16 <3",
    "16": "Hidden FAT16",
    "17": "Hidden HPFS/NTF",
    "18": "AST SmartSleep",
    "1b": "Hidden W95 FAT3",
    "1c": "Hidden W95 FAT3",
    "1e": "Hidden W95 FAT1",
    "24": "NEC DOS",
    "27": "Hidden NTFS Win",
    "39": "Plan 9",
    "3c": "PartitionMagic",
    "40": "Venix 80286",
    "41": "PPC PReP Boot",
    "42": "SFS",
    "4d": "QNX4.x",
    "4e": "QNX4.x 2nd part",
    "4f": "QNX4.x 3rd part",
    "50": "OnTrack DM",
    "51": "OnTrack DM6 Aux",
    "52": "CP/M",
    "53": "OnTrack DM6 Aux",
    "54": "OnTrackDM6",
    "55": "EZ-Drive",
    "56": "Golden Bow",
    "5c": "Priam Edisk",
    "61": "SpeedStor",
    "63": "GNU HURD or Sys",
    "64": "Novell Netware",
    "65": "Novell Netware",
    "70": "DiskSecure Mult",
    "75": "PC/IX",
    "80": "Old Minix",
    "81": "Minix / old Lin",
    "82": "Linux swap / So",
    "83": "Linux",
    "84": "OS/2 hidden C:",
    "85": "Linux extended",
    "86": "NTFS volume set",
    "87": "NTFS volume set",
    "88": "Linux plaintext",
    "8e": "Linux LVM",
    "93": "Amoeba",
    "94": "Amoeba BBT",
    "9f": "BSD/OS",
    "a0": "IBM Thinkpad hi",
    "a5": "FreeBSD",
    "a6": "OpenBSD",
    "a7": "NeXTSTEP",
    "a8": "Darwin UFS",
    "a9": "NetBSD",
    "ab": "Darwin boot",
    "af": "HFS / HFS+",
    "b7": "BSDI fs",
    "b8": "BSDI swap",
    "bb": "Boot Wizard hid",
    "be": "Solaris boot",
    "bf": "Solaris",
    "c1": "DRDOS/sec (FAT-",
    "c4": "DRDOS/sec (FAT-",
    "c6": "DRDOS/sec (FAT-",
    "c7": "Syrinx",
    "da": "Non-FS data",
    "db": "CP/M / CTOS / .",
    "de": "Dell Utility",
    "df": "BootIt",
    "e1": "DOS access",
    "e3": "DOS R/O",
    "e4": "SpeedStor",
    "eb": "BeOS fs",
    "ee": "GPT",
    "ef": "EFI (FAT-12/16/",
    "f0": "Linux/PA-RISC b",
    "f1": "SpeedStor",
    "f4": "SpeedStor",
    "f2": "DOS secondary",
    "fb": "VMware VMFS",
    "fc": "VMware VMKCORE",
    "fd": "Linux raid auto",
    "fe": "LANstep",
    "ff": "BBT"
}

def process_data_file():
    file = sys.argv[1]

    with open(file, "rb") as f:
        for i in range(446):
            boot_strap.append(f.read(1).hex())
        for i in range(16):
            part_1.append(f.read(1).hex())
        for i in range(16):
            part_2.append(f.read(1).hex())
        for i in range(16):
            part_3.append(f.read(1).hex())
        for i in range(16):
            part_4.append(f.read(1).hex())
        for i in range(2):
            boot_rcd_sig.append(f.read(1).hex())

# returns the file name, without the path or extension
def extract_name_from_path(f):
    fileName = os.path.basename(f)
    name_only = fileName.split('.')[0]
    return name_only

# generates sha1 and md5 checksums of raw image file
def generate_hashes():

    file_name = os.path.basename(sys.argv[1]).split('.')[0]
    file_extension = os.path.basename(sys.argv[1]).split('.')[1]

    entire_file_name = f"{file_name}.{file_extension}"
    
    BUF_SIZE = 65536

    md5 = hashlib.md5()
    sha1 = hashlib.sha1()

    with open(sys.argv[1], 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
            sha1.update(data)

    #print("MD5: {0}".format(md5.hexdigest()))
    #print("sha1: {0}".format(sha1.hexdigest()))

    f = open(f"SHA1-{entire_file_name}.txt", "w")
    f.write(sha1.hexdigest())
    f.close()

    f = open(f"MD5-{entire_file_name}.txt", "w")
    f.write(md5.hexdigest())
    f.close()


def get_last_8_bytes(end_address):
    file = sys.argv[1]
    l = []
    with open(file, "rb") as f:
       
            for i in range(end_address - 8):
                f.read(1)
            for i in range(8):
                l.append(f.read(1).hex())

    return l

    

def extract_partition_data(part_list):

    start_sector = ""
    part_size = ""

    flag = part_list[0]
    part_type = part_list[4]
    for i in range(11, 7, -1):
        start_sector = start_sector + part_list[i]
    for i in range(15, 11, -1):
        part_size = part_size + part_list[i]

    start_sector_decimal = int(start_sector, 16)
    part_size_decimal = int(part_size, 16)

    start_address = start_sector_decimal * 512
    #print(f"start sector decimal {start_sector_decimal}")
    #print(f"start sector hex {start_sector}")

    end_address = part_size_decimal * 512 + start_address
    last8 = get_last_8_bytes(end_address)
    
    #print(f"Size of partition: {part_size_decimal}")
    #print(f"start addr: {start_address}")
    #print(f"end addr: {end_address}")
    

    return [flag, part_type, str(start_sector_decimal).zfill(10), str(part_size_decimal).zfill(10), last8, part_type!='00']

def print_partition_data(l):
    if l[5]:
        print(f"({l[1]}) {partitions_types_dict.get(l[1])}, {l[2]}, {l[3]}")


def print_last_8_bytes(part_number,l, active):
    if active:
        print(f"Partition number: {part_number}")
        print("Last 8 bytes of boot record: ", end="")
        for i in l:
            print(i, end=" ")
        print()


# creates hash checksum text files
generate_hashes()
# read bytes and stores to appropiate lists
process_data_file()

p1 = extract_partition_data(part_1)
p2 = extract_partition_data(part_2)
p3 = extract_partition_data(part_3)
p4 = extract_partition_data(part_4)


print_partition_data(p1)
print_partition_data(p2)
print_partition_data(p3)
print_partition_data(p4)

print_last_8_bytes(1, p1[4], p1[5])
print_last_8_bytes(2, p2[4], p2[5])
print_last_8_bytes(3, p3[4], p3[5])
print_last_8_bytes(4, p4[4], p4[5])
