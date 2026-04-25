from database.mysql_db import get_db_connection

def create_new_project(user_id, project_name):
    """
    Tạo dự án mới trong bảng Du_An và trả về ID vừa tạo.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Truyền đầy đủ các cột bắt buộc (NOT NULL) với giá trị mặc định
        sql = """
            INSERT INTO Du_An
            (ID_User, TenDuAn, CongSuat_Tai_W, TocDo_Tai_vph, NamPhucVu, SoNgay_Nam, SoCa_Ngay, CheDoTai)
            VALUES (%s, %s, 0, 0, 0, 0, 0, '')
        """
        cursor.execute(sql, (user_id, project_name))

        project_id = cursor.lastrowid
        conn.commit()

        print(f"DEBUG: Project created with ID {project_id} for user {user_id}")
        return project_id
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error creating project: {e}")
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
