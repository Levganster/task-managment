document.addEventListener("DOMContentLoaded", function() {
    if (currentUser) {
        loadTasks();

        const createTaskForm = document.getElementById('create-task-form');
        if (createTaskForm) {
            createTaskForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                const title = document.getElementById('title').value;
                const description = document.getElementById('description').value;

                const response = await fetch('/tasks/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ title, description }),
                    credentials: 'include'
                });

                if (response.ok) {
                    location.reload();
                } else {
                    alert('Ошибка при создании задачи');
                }
            });
        }
    }
});

async function loadTasks() {
    const response = await fetch('/tasks/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include'
    });

    if (response.ok) {
        const tasks = await response.json();
        const container = document.getElementById('tasks-container');
        container.innerHTML = '';

        tasks.forEach(task => {
            const taskCard = document.createElement('div');
            taskCard.className = 'card task-card' + (task.completed ? ' completed' : '');
            taskCard.innerHTML = `
                <div class="card-body">
                    <div class="form-check">
                        <input class="form-check-input checkbox" type="checkbox" id="task-${task.id}" ${task.completed ? 'checked' : ''} onclick="toggleComplete(${task.id})">
                        <label class="form-check-label" for="task-${task.id}">
                            <h5 class="card-title">${task.title}</h5>
                        </label>
                    </div>
                    <p class="card-text">${task.description || ''}</p>
                    <p class="card-text"><small class="text-muted">Добавил: ${task.owner.username}</small></p>
                    <button class="btn btn-warning btn-sm" onclick="editTask(${task.id})">Редактировать</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteTask(${task.id})">Удалить</button>
                </div>
            `;
            container.appendChild(taskCard);
        });
    } else {
        alert('Ошибка при загрузке задач');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Вы уверены, что хотите удалить эту задачу?')) {
        return;
    }

    const response = await fetch(`/tasks/${taskId}`, {
        method: 'DELETE',
        credentials: 'include'
    });

    if (response.ok) {
        location.reload();
    } else {
        alert('Ошибка при удалении задачи');
    }
}

async function editTask(taskId) {
    const newTitle = prompt("Введите новое название задачи:");
    if (newTitle === null) return;

    const newDescription = prompt("Введите новое описание задачи:");

    const response = await fetch(`/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title: newTitle, description: newDescription }),
        credentials: 'include'
    });

    if (response.ok) {
        location.reload();
    } else {
        alert('Ошибка при обновлении задачи');
    }
}

async function toggleComplete(taskId) {
    const response = await fetch(`/tasks/${taskId}/complete`, {
        method: 'PATCH',
        credentials: 'include'
    });

    if (response.ok) {
        const taskCard = document.getElementById(`task-${taskId}`).closest('.task-card');
        taskCard.classList.toggle('completed');
    } else {
        alert('Ошибка при обновлении статуса задачи');
    }
}