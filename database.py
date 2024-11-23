from mysql.connector import Error
import mysql.connector

def create_connection(host_name, user_name, user_password, database_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=database_name
        )
        print("Connection successful")
    except Error as e:
        print(f"Error: {e}")
    return connection


def add_event(connection, event_name_id, sport_id, name, gender_age, description, structure, start, end, address, count):
    cursor = connection.cursor()
    query = '''
        INSERT INTO events (event_name_id, sport_id, name, gender_age, description, structure, start, end, address, count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    cursor.execute(query, (event_name_id, sport_id, name, gender_age, description, structure, start, end, address, count))
    connection.commit()
    cursor.close()
    print(f'event {event_name_id} added')


def get_event_by_id(connection, event_name_id):
    cursor = connection.cursor()
    query = "SELECT * FROM events WHERE event_name_id = %s"
    cursor.execute(query, (event_name_id,))
    record = cursor.fetchone()
    cursor.close()
    return record

def get_all_events(connection):
    cursor = connection.cursor()
    query = "SELECT event_name_id FROM events"
    cursor.execute(query)
    event_ids = cursor.fetchall()
    cursor.close()
    return [event_name_id[0] for event_name_id in event_ids]

def get_all_sports(connection):
    cursor = connection.cursor()
    query = "SELECT sport_id FROM sports"
    cursor.execute(query)
    sport_ids = cursor.fetchall()
    cursor.close()
    return [sport_id[0] for sport_id in sport_ids]

def update_record(connection, event_name_id, sport_id, name, gender_age, description, structure, start, end, address, count):
    cursor = connection.cursor()
    query = '''
        UPDATE events 
        SET sport_id = %s, name = %s, gender_age = %s, description = %s, structure = %s, start = %s, end = %s, address = %s, count = %s 
        WHERE event_name_id = %s
    '''
    cursor.execute(query, (sport_id, name, gender_age, description, structure, start, end, address, count, event_name_id))
    connection.commit()
    cursor.close()
    print(f'event {event_name_id} updated')

def delete_event(connection, event_name_id):
    cursor = connection.cursor()
    query = "DELETE FROM events WHERE event_name_id = %s"
    cursor.execute(query, (event_name_id,))
    connection.commit()
    cursor.close()
    print(f'event {event_name_id} deleted')

def delete_all_events(connection):
    cursor = connection.cursor()
    query = "DELETE FROM events"
    cursor.execute(query)
    connection.commit()
    cursor.close()
    print(f'all events deleted')

def add_sport(connection, sport_id, name):
    cursor = connection.cursor()
    query = "INSERT INTO sports (sport_id, name) VALUES (%s, %s)"
    cursor.execute(query, (sport_id, name))
    connection.commit()
    cursor.close()
    print(f'sport{sport_id} added')

def get_sport_by_id(connection, sport_id):
    cursor = connection.cursor()
    query = "SELECT * FROM sports WHERE sport_id = %s"
    cursor.execute(query, (sport_id,))
    record = cursor.fetchone()
    cursor.close()
    return record






