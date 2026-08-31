"""
utils/show_mongo_structure.py

AutoSearch V4

用途：
    只顯示 MongoDB 儲存結構。

注意：
    不連線 MongoDB
    不查詢資料
    不顯示實際內容
"""


def show_mongo_structure():
    structure = """
MongoDB
└── snapshots
    └── {
        _id
        url
        created_at
        html
        content_hash
        mime_type
        file_size

        resources
        ├── css[]
        │   ├── url
        │   ├── content
        │   ├── content_hash
        │   ├── mime_type
        │   └── file_size
        │
        └── images[]
            ├── url
            ├── data
            ├── content_hash
            ├── mime_type
            └── file_size
    }
"""

    print(structure)


if __name__ == "__main__":
    show_mongo_structure()