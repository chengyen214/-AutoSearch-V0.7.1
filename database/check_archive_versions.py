from database.connection import get_connection


def main():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        print("=" * 70)
        print("ARCHIVE_VERSIONS SCHEMA")
        print("=" * 70)

        cursor.execute(
            """
            SHOW COLUMNS FROM archive_versions
            """
        )

        columns = cursor.fetchall()

        for column in columns:
            print(column)

        print()
        print("=" * 70)
        print("CREATE TABLE archive_versions")
        print("=" * 70)

        cursor.execute(
            """
            SHOW CREATE TABLE archive_versions
            """
        )

        result = cursor.fetchone()

        if result:
            print(
                result["Create Table"]
            )

        print()
        print("=" * 70)
        print("ARCHIVE_VERSIONS DATA")
        print("=" * 70)

        cursor.execute(
            """
            SELECT *
            FROM archive_versions
            ORDER BY id ASC
            """
        )

        rows = cursor.fetchall()

        if not rows:

            print("No archive_versions data.")

        else:

            for index, row in enumerate(
                rows,
                start=1
            ):

                print()
                print(f"[{index}]")

                for key, value in row.items():

                    print(
                        f"{key}: {value}"
                    )

    finally:

        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()