def updating_table(table_name, conn, new_value, data):
    with conn.cursor() as cursor:
        for key, value in data.items():
            try:
                cursor.execute(f""" update {table_name}
                                set {key} = '{new_value}' 
                                WHERE {key} = '{value}'""")
                print(f'in table "{table_name}":\n in column "{key}" meaning "{value}" was changed in "{new_value}"')

            except Exception:
                print("some troubles try to check data!")
