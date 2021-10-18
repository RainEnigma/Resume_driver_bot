def join_tab(connection, tab_1, tab_2, category):
    with connection.cursor() as cursor:
        cursor.execute(f""" SELECT * FROM {tab_1}
                        INNER JOIN {tab_2}
                        ON {tab_1}.{category} = {tab_2}.{category}
             """)
        return cursor.fetchall()
