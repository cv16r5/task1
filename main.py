import json
import boto3
import re
import os
import csv
from collections import Counter
import uuid

BUCKET_NAME = "bukcet-text-analysis"


class TextAnalysis:
    """
    Class with methods to extracts strings and numbers from the request.
    Save result as files csv and json with hash name ("uuid.uuid1()").
    """

    def __init__(self, row_text, bucket_name=None):
        # result list with fib number
        self.result = []
        self.analyzed_text = row_text
        self.bucket, self.s3 = None, None
        self.bucket_name = bucket_name
        self.file_name = uuid.uuid1()

    def analyzed(self):
        """
        The main method runs all tasks.
        """
        self.create_s3()
        numbers = self.get_numbers(self.analyzed_text)
        fib_list = self.fib(max(numbers))
        self.check_fib(numbers, fib_list)
        self.save_csv()
        self.get_words_save(self.analyzed_text)

    def check_fib(self, numbers, fib_list):
        """
        Add the previous and following numbers of the fibonacci seq (if the number is a part of the seq)
        to the 'self.result'.

        :param numbers: list of numbers from the input
        :param fib_list: list with fibonacci numbers
        :return:
        """
        for n in numbers:
            if n in fib_list:
                _id = fib_list.index(n)
                if n == 0:
                    _id = 1
                self.result.append([fib_list[_id - 1], n, fib_list[_id + 1]])
            else:
                self.result.append([None, n, None])

    @staticmethod
    def fib(n):
        """
        Create a list of fibonacci numbers one greater than the parameter n.

        :param n: max number
        :return: list with fibonacci numbers
        """
        if n <= 0:
            return [0]
        seq = [0, 1]
        while max(seq) <= n:
            seq.append(seq[len(seq) - 1] + seq[len(seq) - 2])
        return seq

    def get_words_save(self, txt):
        """
        Finds all words containing only alphabetical characters, counts the number of word occurrences.

        :param txt: string from input
        :return: None
        """
        words = [w.lower() for w in re.findall("[a-zA-Z]+", txt)]
        dict_words = Counter(words)
        self.save_json(dict_words)

    @staticmethod
    def get_numbers(txt):
        """
        Finds all integers in the input text, saves them in ascending order.

        :param txt: string from input
        :return: list of strings
        """
        numbers = list(set(int(n) for n in re.findall(r'\d+', txt)))
        numbers.sort()
        return numbers

    def create_s3(self):
        """
        Create connection to s3 bucket.
        """
        self.s3 = boto3.resource('s3')
        self.bucket = self.s3.Bucket(self.bucket_name)

    def save_json(self, data):
        """
        Saves data to a json file.

        :param data: dict of data
        """
        #
        upload_byte_dict = bytes(json.dumps(data).encode('utf8'))
        self.bucket.put_object(Bucket=self.bucket_name, Key=f'{self.file_name}.json', Body=upload_byte_dict)

    def save_csv(self):
        """
        Saves data (list of tuples) to a csv file.
        """
        full_path = os.path.join("/tmp/", f'{self.file_name}.csv')
        with open(full_path, 'w', newline='') as f:
            csv_out = csv.writer(f)
            csv_out.writerow(['previos Fibonacci number', 'observed number', 'next Fibonacci number'])
            for row in self.result:
                csv_out.writerow(row)
        self.bucket.upload_file(full_path, Key=f'{self.file_name}.csv')


def lambda_handler(event, context):
    try:
        raw_text = event['body']
        obj = TextAnalysis(raw_text, bucket_name=BUCKET_NAME)
        obj.analyzed()

        return {
            'statusCode': 200,
            'body': "Successful, the text was analyzed and saved in files"
        }
    except Exception as e:
        print(f"Issue while text-analysis: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Issue while text-analysis')
        }
