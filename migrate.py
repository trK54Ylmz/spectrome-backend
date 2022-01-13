from db.migration import Migration

if __name__ == '__main__':
    m = Migration()

    # migrate table to selected database
    m.migrate()
