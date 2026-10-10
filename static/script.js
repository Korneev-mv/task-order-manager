document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "/static/login.html";
        return;
    }

    document.getElementById("logoutBtn").addEventListener("click", () => {
        localStorage.removeItem("token");
        window.location.href = "/static/login.html";
    });

    async function loadOrders() {
        const res = await fetch("/orders/me", {
            headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) return;
        const orders = await res.json();
        const container = document.getElementById("ordersList");
        if (!orders.length) {
            container.innerHTML = "<p>Пока нет заказов</p>";
            return;
        }
        container.innerHTML = orders
            .map(
                (o) => `
            <div class="card">
              <strong>Заказ #${o.id}</strong><br />
              Сумма: ${o.amount} ₽<br />
              Дата: ${o.created_at}
            </div>
          `
            )
            .join("");
    }

    async function loadTasks() {
        const res = await fetch("/tasks", {
            headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) return;
        const tasks = await res.json();
        const container = document.getElementById("tasksList");
        if (!tasks.length) {
            container.innerHTML = "<p>Пока нет задач</p>";
            return;
        }
        container.innerHTML = tasks
            .map(
                (t) => `
            <div class="card task-card" data-id="${t.id}">
              <strong>${t.title}</strong><br />
              ${t.description || "—"}<br />
              Статус: <span class="status status-${t.status}">${t.status}</span><br />
              <button class="btn-delete" data-id="${t.id}">🗑 Удалить</button>
              <button class="btn-toggle" data-id="${t.id}">🔄 Сменить статус</button>
            </div>
          `
            )
            .join("");

        document.querySelectorAll(".btn-delete").forEach((btn) => {
            btn.addEventListener("click", async (e) => {
                const id = e.target.dataset.id;
                await fetch(`/tasks/${id}`, {
                    method: "DELETE",
                    headers: { Authorization: `Bearer ${token}` },
                });
                loadTasks();
            });
        });

        document.querySelectorAll(".btn-toggle").forEach((btn) => {
            btn.addEventListener("click", async (e) => {
                const id = e.target.dataset.id;
                const statuses = ["todo", "in_progress", "done"];
                const current = document
                    .querySelector(`.task-card[data-id="${id}"] .status`)
                    .textContent.trim();
                const nextIndex = (statuses.indexOf(current) + 1) % statuses.length;
                const newStatus = statuses[nextIndex];
                await fetch(`/tasks/${id}`, {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                    body: JSON.stringify({ status: newStatus }),
                });
                loadTasks();
            });
        });
    }

    document.getElementById("showOrderFormBtn").addEventListener("click", () => {
        const container = document.getElementById("orderFormContainer");
        container.style.display = container.style.display === "none" ? "block" : "none";
    });

    document.getElementById("createOrderBtn").addEventListener("click", async () => {
        const amount = document.getElementById("orderAmount").value;
        if (!amount) return alert("Введите сумму");
        const res = await fetch("/orders/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ amount: parseFloat(amount) }),
        });
        if (res.ok) {
            document.getElementById("orderAmount").value = "";
            document.getElementById("orderFormContainer").style.display = "none";
            loadOrders();
        } else {
            alert("Ошибка при создании заказа");
        }
    });

    document.getElementById("showTaskFormBtn").addEventListener("click", () => {
        const container = document.getElementById("taskFormContainer");
        container.style.display = container.style.display === "none" ? "block" : "none";
    });

    document.getElementById("createTaskBtn").addEventListener("click", async () => {
        const title = document.getElementById("taskTitle").value;
        const description = document.getElementById("taskDescription").value;
        const status = document.getElementById("taskStatus").value;
        if (!title) return alert("Введите название");
        const res = await fetch("/tasks/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ title, description, status }),
        });
        if (res.ok) {
            document.getElementById("taskTitle").value = "";
            document.getElementById("taskDescription").value = "";
            document.getElementById("taskFormContainer").style.display = "none";
            loadTasks();
        } else {
            alert("Ошибка при создании задачи");
        }
    });

    loadOrders();
    loadTasks();
});