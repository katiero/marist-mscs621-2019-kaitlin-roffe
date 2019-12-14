######################################################################
# Copyright 2018 Jinho Hwang. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################
"""
Data Model that uses Redis

You must initlaize this class before use by calling inititlize().
This class looks for an environment variable called VCAP_SERVICES
to get it's database credentials from. If it cannot find one, it
tries to connect to Redis on the localhost. If that fails it looks
for a server name 'redis' to connect to.
"""

import os
import json
import logging
import pickle
from redis import Redis
from redis.exceptions import ConnectionError

class DataValidationError(Exception):
    """ Custom Exception with data validation fails """
    pass

class Data(object):
    """ Data interface to database """

    logger = logging.getLogger(__name__)
    redis = None

    def __init__(self, id=0, gift=None, gifter=None, thanked=None):
        """ Constructor """
        self.id = int(id)
        self.gift = gift
        self.gifter = gifter
        self.thanked = thanked

    def save(self):
        """ Saves a Data in the database """
        if self.gift is None:   # gift is the only required field
            raise DataValidationError('gift attribute is not set')
        if self.id == 0:
            self.id = Data.__next_index()
        Data.redis.set(self.id, pickle.dumps(self.serialize()))

    def delete(self):
        """ Deletes a Data from the database """
        Data.redis.delete(self.id)

    def serialize(self):
        """ serializes a Data into a dictionary """
        return {
            "id": self.id,
            "gift": self.gift,
            "gifter": self.gifter,
            "thanked":self.thanked,
        }

    def deserialize(self, data):
        """ deserializes a Data my marshalling the data """
        try:
            self.gift = data['gift']
            self.gifter = data['gifter']
            self.thanked = data['thanked']
        except KeyError as error:
            raise DataValidationError('Invalid data: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid data: body of request contained bad or no data')
        return self

######################################################################
#  S T A T I C   D A T A B S E   M E T H O D S
######################################################################

    @staticmethod
    def __next_index():
        """ Increments the index and returns it """
        return Data.redis.incr('index')

    @staticmethod
    def remove_all():
        """ Removes all Datas from the database """
        Data.redis.flushall()

    @staticmethod
    def all():
        """ Query that returns all Datas """
        # results = [Data.from_dict(redis.hgetall(key)) for key in redis.keys() if key != 'index']
        results = []
        for key in Data.redis.keys():
            if key != 'index':  # filer out our id index
                data = pickle.loads(Data.redis.get(key))
                data = Data(data['id']).deserialize(data)
                results.append(data)
        return results

######################################################################
#  F I N D E R   M E T H O D S
######################################################################

    @staticmethod
    def find(data_id):
        """ Query that finds Datas by their id """
        if Data.redis.exists(data_id):
            data = pickle.loads(Data.redis.get(data_id))
            data = Data(data['id']).deserialize(data)
            return data 
        return None

    @staticmethod
    def __find_by(attribute, value):
        """ Generic Query that finds a key with a specific value """
        Data.logger.info('Processing %s query for %s', attribute, value)
        if isinstance(value, str):
            search_criteria = value.lower() # make case insensitive
        else:
            search_criteria = value
        results = []
        for key in Data.redis.keys():
            if key != 'index':  # filer out our id index
                data = pickle.loads(Data.redis.get(key))
                # perform case insensitive search on strings
                if isinstance(data[attribute], str):
                    test_value = data[attribute].lower()
                else:
                    test_value = data[attribute]
                if test_value == search_criteria:
                    results.append(Data(data['id']).deserialize(data))
        return results

    @staticmethod
    def find_by_gift(gift):
        """ Query that finds Datas by gift """
        return Data.__find_by('gift', gift)
    
    @staticmethod
    def find_by_gifter(gifter):
        """ Query that finds Datas by gifter """
        return Data.__find_by('gifter', gifter)

    @staticmethod
    def find_by_thanked(thanked):
        """ Query that finds Datas by their category """
        return Data.__find_by('thanked', thanked)

######################################################################
#  R E D I S   D A T A B A S E   C O N N E C T I O N   M E T H O D S
######################################################################

    @staticmethod
    def connect_to_redis(hostname, port, password):
        """ Connects to Redis and tests the connection """
        Data.logger.info("Testing Connection to: %s:%s", hostname, port)
        Data.redis = Redis(host=hostname, port=port, password=password)
        try:
            Data.redis.ping()
            Data.logger.info("Connection established")
        except ConnectionError:
            Data.logger.info("Connection Error from: %s:%s", hostname, port)
            Data.redis = None
        return Data.redis

    @staticmethod
    def init_db(redis=None):
        """
        Initialized Redis database connection

        This method will work in the following conditions:
          1) With Redis --link in a Docker container called 'redis'
          2) With Redis Enterprise Cloud

        Exception:
        ----------
          redis.ConnectionError - if ping() test fails
        """
        # Docker
        if redis:
            Data.logger.info("Using client connection...")
            Data.redis = redis
            try:
                Data.redis.ping()
                Data.logger.info("Connection established")
            except ConnectionError:
                Data.logger.error("Client Connection Error!")
                Data.redis = None
                raise ConnectionError('Could not connect to the Redis Service')
            return
        # Redis Enterprise Cloud
        if not redis:
            hostname='EnterHostAddressHere'
            port=16771
            password='EnterPasswordHere'
            Data.logger.info("Testing Connection to: %s:%s", hostname, port)
            Data.redis = Redis(host=hostname, port=port, password=password)
            try:
                Data.redis.ping()
                Data.logger.info("Connection established")
            except ConnectionError:
                Data.logger.info("Connection Error from: %s:%s", hostname, port)
                Data.redis = None
            return Data.redis
        if not Data.redis:
            # if you end up here, redis instance is down.
            Data.logger.fatal('*** FATAL ERROR: Could not connect to the Redis Service')
            raise ConnectionError('Could not connect to the Redis Service')
