from app.db.database import get_db_connection
from fastapi import HTTPException
from app.models.schemas import TaskCreate, TaskUpdate, TaskResponse, UserTasksStats
from datetime import datetime

async def insert_task(user_id: int, task_data: TaskCreate) -> TaskResponse:
    async with get_db_connection() as connection:
        cursor = await connection.cursor()
        status = task_data.status or "todo"
        await cursor.execute('''
        INSERT INTO tasks (user_id, title, description, status) VALUES (?, ?, ?, ?)
        ''', [user_id, task_data.title, task_data.description, status])
        await connection.commit()
        last_id = cursor.lastrowid
        await cursor.execute('''SELECT * FROM tasks WHERE id = ?''', [last_id])
        new_task = await cursor.fetchone()

        task = TaskResponse(id=new_task[0], user_id=new_task[1], title=new_task[2], description=new_task[3],
                            status=new_task[4], created_at=new_task[5],
                            updated_at=new_task[6])
        return task

async def get_tasks_by_user(user_id: int) -> list[TaskResponse]:
    async with get_db_connection() as connection:
        cursor = await connection.cursor()
        await cursor.execute('''
        SELECT * FROM tasks WHERE user_id = ?
        ''', [user_id])
        tasks = await cursor.fetchall()
        return [TaskResponse(id=task[0], user_id=task[1], title=task[2], description=task[3],
                            status=task[4], created_at=task[5],
                            updated_at=task[6]) for task in tasks]

async def get_task_by_id(task_id: int, user_id: int) -> TaskResponse  | None:
    async with get_db_connection() as connection:
        cursor = await connection.cursor()
        await cursor.execute('''
        SELECT * FROM tasks WHERE id = ? AND user_id = ?
        ''', [task_id, user_id])
        task = await cursor.fetchone()
        if task is None:
            return None

        return TaskResponse(id=task[0], user_id=task[1], title=task[2], description=task[3],
                            status=task[4], created_at=task[5],
                            updated_at=task[6])


async def update_task_by_id(task_id: int, user_id: int, task_data: TaskUpdate) -> TaskResponse | None:
    async with get_db_connection() as connection:
        cursor = await connection.cursor()
        await cursor.execute('''SELECT * FROM tasks where id = ? AND user_id = ?''', [task_id, user_id])
        task = await cursor.fetchone()
        if task is None:
            return None

        task_to_update = [task_data.title, task_data.description, task_data.status]
        for _ in range(len(task_to_update)):
            if None in task_to_update:
                if task_to_update[0] is None:
                    task_to_update[0] = task[2]
                elif task_to_update[1] is None:
                    task_to_update[1] = task[3]
                else:
                    task_to_update[2] = task[4]

        await cursor.execute('''
        UPDATE tasks SET title = ?, description = ?, status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
        ''', [task_to_update[0], task_to_update[1], task_to_update[2], task_id, user_id])
        await connection.commit()

        await cursor.execute('''SELECT * FROM tasks WHERE id = ?''', [task_id])
        updated_task = await cursor.fetchone()
        return TaskResponse(id=updated_task[0], user_id=updated_task[1], title=updated_task[2], description=updated_task[3],
                            status=updated_task[4], created_at=updated_task[5],
                            updated_at=updated_task[6])




async def delete_task_by_id(task_id: int, user_id: int) -> bool:
    async with get_db_connection() as connection:
        cursor = await connection.cursor()
        await cursor.execute('''
        DELETE FROM tasks WHERE id = ? AND user_id = ?
        ''', [task_id, user_id])
        await connection.commit()
        return cursor.rowcount > 0


async def get_top_users_by_tasks(limit: int = 5) -> list[UserTasksStats]:
    async with get_db_connection() as connection:
        cursor = await connection.cursor()
        await cursor.execute('''
        SELECT u.id, u.name, COUNT(*) AS tasks_done FROM
        users u JOIN tasks t ON u.id = t.user_id
        WHERE t.status = 'done'
        GROUP BY user_id
        ORDER BY tasks_done DESC
        LIMIT ? 
        ''', [limit])
        tops = await cursor.fetchall()
        return [
            UserTasksStats(user_id = top[0], name = top[1], tasks_done = top[2]) for top in tops
        ]