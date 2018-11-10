from collections import Counter
from datetime import datetime
import json
import os
import sys
import time


class transaction:

    def __init__(self, json_str):
        self.next = None
        data = json.loads(json_str)
        time_value = str(data['created_time'])
        self.time = datetime.strptime(time_value, '%Y-%m-%dT%H:%M:%SZ')
        self.target = data['target']
        self.actor = data['actor']

        if self.target == '' or self.actor == '':
            raise ValueError

##putting transaction into linked list
def insert(insert_transaction, previous_transaction, next_transaction, first_transaction):
    if previous_transaction:
        previous_transaction.next = insert_transaction
    else:
        first_transaction = insert_transaction

    insert_transaction.next = next_transaction
    return first_transaction

## output in desired format
def output_append(output, n):
    output += "{0:.2f}\n".format(n)
    return output


def process(input_file, output_file):
    if not os.path.exists(input_file):
        print('Input file does not exist!')
        return

    first_transaction = None  
    window_end = None  
    last_median = None  
    output = '' 

    f = open(input_file)

    for line in f:
        try:
            new_transaction = transaction(line)
        except ValueError:
            continue
        except KeyError:
            continue

        if not window_end or new_transaction.time > window_end:
            window_end = new_transaction.time
        elif (window_end - new_transaction.time).seconds > 60:
            output = output_append(output, last_median)
            continue

        payments = Counter()
        payments[new_transaction.actor] += 1
        payments[new_transaction.target] += 1

        
        current_transaction = first_transaction
        last_transaction = None

        duplicate_found = False
        should_insert = True
        found_insertion_point = False
        insert_before = None  
        insert_after = None  
        
        while current_transaction:
            if (window_end - current_transaction.time).seconds > 60:
                first_transaction = current_transaction.next

            else:
                if (current_transaction.target == new_transaction.target and \
                        current_transaction.actor == new_transaction.actor) or \
                    (current_transaction.actor == new_transaction.target and \
                        current_transaction.target == new_transaction.actor):
                    duplicate_found = True

                    if current_transaction.time >= new_transaction.time:
                        should_insert = False
                        break
                    else:
                        current_transaction = current_transaction.next

                        if last_transaction:
                            last_transaction.next = current_transaction
                        else:
                            first_transaction = current_transaction

                        if not current_transaction:
                            insert_before = last_transaction
                            break
                        continue

                else:
                    payments[current_transaction.target] += 1
                    payments[current_transaction.actor] += 1
                    
                    if not found_insertion_point and current_transaction.time >= new_transaction.time:
                        insert_before = last_transaction
                        insert_after = current_transaction

                        found_insertion_point = True

                        if duplicate_found:
                            break

                last_transaction = current_transaction

            current_transaction = current_transaction.next

        if should_insert:
            insert_before = insert_before if found_insertion_point else last_transaction
            first_transaction = insert(new_transaction, insert_before, insert_after, first_transaction)

        if not duplicate_found:
            vertex_degrees = payments.most_common()
            n = len(vertex_degrees)
            halfway = int(n / 2)
            if n % 2:
                last_median = vertex_degrees[halfway][1]
            else:
                last_median = (vertex_degrees[halfway][1] + vertex_degrees[halfway - 1][1]) / 2.0

        output = output_append(output, last_median)

    folder = os.path.split(output_file)[0]
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(output_file, 'w') as f:
        f.write(output)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Wrong argument/input')
    else:
        process(sys.argv[1], sys.argv[2])
