from functions.custom.config import encrypt, decrypt, customs_func
from modules.setting import SettingModule
from modules.testing import TestingModule
from modules.option import OptionModule
from tornado.web import app_log as log
from tornado import gen
from munch import munchify
import json
import re


# 获取配置类
class OptionsFunction(object):
    def __init__(self):
        self.setting = SettingModule()
        self.option = OptionModule()

    # 通过名称获取系统配置值
    @gen.coroutine
    def get_option_by_name(self, name):
        option = yield self.option.get_option(name=name)
        if option:
            return option.value
        else:
            return ''

    # 获取加解密参数
    @gen.coroutine
    def get_crypt_info(self, pid, do='encrypt'):
        setting, total = yield self.setting.get_settings_list(pid=pid, s_type='crypt', limit=None)
        setting = setting[0] if len(setting) > 0 else None
        if setting:
            flag = False
            crypt = json.loads(setting.value)
            if do == 'encrypt':
                crypt = crypt['encrypt']
                for info in encrypt:
                    if info['name'] == crypt['name']:
                        crypt['mode'] = info['mode']
                        crypt['function'] = info['function']
                        flag = True
                        break
            elif do == 'decrypt':
                crypt = crypt['decrypt']
                for info in decrypt:
                    if info['name'] == crypt['name']:
                        crypt['mode'] = info['mode']
                        crypt['function'] = info['function']
                        flag = True
                        break
            if not flag:
                crypt = None
            return munchify(crypt)
        else:
            return None

    # 获取自定义参数配置
    @gen.coroutine
    def get_custom_param(self, pid, correlation={}):
        setting, total = yield self.setting.get_settings_list(pid=pid, s_type='param', limit=None)
        setting = setting[0] if len(setting) > 0 else None
        if setting:
            params_str = []
            params_data = []
            params_func = []
            for row in json.loads(setting.value):
                row = json.loads(row)
                if row['type'] == 'Function':
                    for func in customs_func:
                        if row['value'] == func['name']:
                            row['function'] = func['function']
                            break
                    params_func.append(row)
                elif row['type'] == 'Data':
                    params_data.append(row)
                else:
                    params_str.append(row)
            for key in correlation:
                if not isinstance(correlation[key], str):
                    correlation[key] = str(correlation[key])
            for param in params_str:
                for key in correlation:
                    if param['value'].find(key) != -1:
                        param['value'] = param['value'].replace(key, correlation[key])
            for param in params_data:
                for row in params_str:
                    if param['value'].find('{%s}' % row['name']) != -1:
                        param['value'] = param['value'].replace('{%s}' % row['name'], row['value'])
                for key in correlation:
                    if param['value'].find(key) != -1:
                        param['value'] = param['value'].replace(key, correlation[key])
                argv, do = yield self.parse_sql_argv(param['value'], pid=pid)
                if argv:
                    try:
                        test = TestingModule(**argv)
                        if do == 'SELECT':
                            result = yield test.get_one_result()
                            if result:
                                param['value'] = result[0]
                            else:
                                param['value'] = ''
                        else:
                            raise Exception('目前只支持SELECT方法', do)
                    except Exception as e:
                        log.warning(e)
                        param['value'] = ''
                else:
                    param['value'] = ''
            return params_str + params_data + params_func
        else:
            return []

    # 解析sql参数
    @gen.coroutine
    def parse_sql_argv(self, sql_params, pid=0):
        sql_params = sql_params.splitlines()
        do = ''
        sql_argv = dict()
        if len(sql_params) == 5:
            for line in sql_params:
                line = line.strip().split(sep='=', maxsplit=1)
                if len(line) != 2:
                    return dict(), do
                elif line[0].strip() not in ['mysql', 'user', 'password', 'database', 'sql']:
                    return dict(), do
                elif line[1].strip() == '':
                    return dict(), do
                elif line[0] == 'sql' and re.match(r'^SELECT\s+', line[1].strip().upper()) is not None:
                    do = 'SELECT'
                elif line[0] == 'sql' and re.match(r'^DELETE\s+', line[1].strip().upper()) is not None:
                    do = 'DELETE'
                elif line[0] == 'sql' and re.match(r'^UPDATE\s+', line[1].strip().upper()) is not None:
                    do = 'UPDATE'
                elif line[0] == 'sql' and re.match(r'^INSERT\s+', line[1].strip().upper()) is not None:
                    do = 'INSERT'
                if line[0].strip() in ['mysql']:
                    sql_argv['engine'] = line[0].strip()
                    line[1] = line[1].split(':', maxsplit=1)
                    sql_argv['host'] = line[1][0].strip()
                    ips, total = yield self.setting.get_settings_list(
                        pid=pid, s_type='host', name=sql_argv['host'], pj_status=1, status=1, limit=None)
                    if ips:
                        sql_argv['host'] = ips[0].value
                    sql_argv['port'] = line[1][1].strip() if len(line[1]) == 2 else 3306
                elif line[0].strip() == 'user':
                    sql_argv['user'] = line[1].strip()
                elif line[0].strip() == 'password':
                    sql_argv['password'] = line[1].strip()
                elif line[0].strip() == 'database':
                    sql_argv['database'] = line[1].strip()
                elif line[0].strip() == 'sql':
                    sql_argv['sql'] = line[1].strip()
        if len(sql_argv) == 7 and do in ['SELECT', 'DELETE', 'UPDATE', 'INSERT']:
            return sql_argv, do
        else:
            return dict(), do

    # 获取接口完整性检查配置
    @gen.coroutine
    def get_check_key(self, pid, url):
        setting, total = yield self.setting.get_settings_list(pid=pid, s_type='url', limit=None)
        check_key = ''
        if setting:
            for row in setting:
                row = json.loads(row.value)
                if row['url'] == url:
                    check_key = row['check_key']
                    break
        return check_key
