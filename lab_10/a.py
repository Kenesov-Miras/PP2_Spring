import psycopg2
import csv

class PhoneBook:
    def __init__(self, dbname, user, password, host='localhost'):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host

    def connect(self):
        """Connect to the PostgreSQL database and return the connection object."""
        return psycopg2.connect(
            host=self.host,
            dbname=self.dbname,
            user=self.user,
            password=self.password
        )

    def insert_from_console(self):
        """Insert a user from the console."""
        name = input("Enter name: ")
        phone = input("Enter phone: ")
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (name, phone))
                conn.commit()
        print("User added!")

    def insert_from_csv(self, file_path):
        """Insert users from a CSV file."""
        with self.connect() as conn:
            with conn.cursor() as cur:
                with open(file_path, 'r') as file:
                    reader = csv.reader(file)
                    next(reader)  # Skip the header row
                    for row in reader:
                        cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (row[0], row[1]))
                conn.commit()
        print("CSV data imported!")

    def update_user(self):
        """Update a user's phone number."""
        name = input("Enter the name of the user to update: ")
        new_phone = input("Enter the new phone number: ")
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE phonebook SET phone = %s WHERE name = %s", (new_phone, name))
                conn.commit()
        print("User updated!")

    def query_all(self):
        """Display all users in the phonebook."""
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM phonebook")
                rows = cur.fetchall()
                for row in rows:
                    print(row)

    def query_by_name(self):
        """Search for users by name."""
        name = input("Enter the name to search: ")
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM phonebook WHERE name = %s", (name,))
                rows = cur.fetchall()
                if rows:
                    for row in rows:
                        print(row)
                else:
                    print("No user found with that name.")

    def delete_user(self):
        """Delete a user from the phonebook."""
        name = input("Enter the name of the user to delete: ")
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM phonebook WHERE name = %s", (name,))
                conn.commit()
        print("User deleted!")

class Game:
    def __init__(self, dbname, user, password, host='localhost'):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host

    def connect(self):
        """Connect to the PostgreSQL database and return the connection object."""
        return psycopg2.connect(
            host=self.host,
            dbname=self.dbname,
            user=self.user,
            password=self.password
        )

    def create_user(self):
        """Create a new user for the snake game."""
        username = input("Enter your username: ")
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING id", (username,))
                user_id = cur.fetchone()[0]
                conn.commit()
        print(f"User {username} created with ID {user_id}.")
        return user_id

    def get_or_create_user(self):
        """Check if the user exists or create a new one."""
        username = input("Enter your username: ")
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                user = cur.fetchone()
                if user:
                    print(f"Welcome back, {username}!")
                    return user[0]
                else:
                    return self.create_user()

    def save_score(self, user_id, score, level):
        """Save the score and level of the user."""
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO user_scores (user_id, score, level) VALUES (%s, %s, %s)", (user_id, score, level))
                conn.commit()
        print("Score saved!")

def main():
    # Database credentials
    dbname = "lab10"
    user = "postgres"
    password = "123456789"

    # PhoneBook actions
    phonebook = PhoneBook(dbname, user, password)
    game = Game(dbname, user, password)

    while True:
        print("\nPhoneBook Menu:")
        print("1. Insert (console)")
        print("2. Insert (CSV)")
        print("3. Update user")
        print("4. View all")
        print("5. Search by name")
        print("6. Delete user")
        print("7. Game - Create or find user")
        print("8. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == '1':
            phonebook.insert_from_console()
        elif choice == '2':
            file_path = input("Enter CSV file path: ")
            phonebook.insert_from_csv(file_path)
        elif choice == '3':
            phonebook.update_user()
        elif choice == '4':
            phonebook.query_all()
        elif choice == '5':
            phonebook.query_by_name()
        elif choice == '6':
            phonebook.delete_user()
        elif choice == '7':
            user_id = game.get_or_create_user()
            # Here, you can add logic to play the game, then save the score
            score = int(input("Enter your final score: "))
            level = int(input("Enter your level: "))
            game.save_score(user_id, score, level)
        elif choice == '8':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
