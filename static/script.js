const API_BASE = 'http://localhost:8000';

let currentSection = 'users';

function showSection(sectionName) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    document.getElementById(sectionName).classList.add('active');
    currentSection = sectionName;

    // Автоматическая загрузка данных при переключении на вкладку
    switch (sectionName) {
        case 'users':
            loadUsers();
            break;
        case 'accounts':
            loadAccounts();
            break;
        case 'categories':
            loadCategories();
            break;
        case 'transactions':
            loadTransactions();
            loadAccountsForSelect();
            loadCategoriesForSelect();
            break;
        case 'budgets':
            loadBudgets();
            loadCategoriesForBudgetSelect();
            break;
        case 'reports':
            // Отчеты загружаются по кнопкам
            break;
    }
}

async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`${API_BASE}${endpoint}`, options);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        showError(`Ошибка: ${error.message}`);
        return null;
    }
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = message;
    document.querySelector('.section.active').appendChild(errorDiv);

    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success';
    successDiv.textContent = message;
    document.querySelector('.section.active').appendChild(successDiv);

    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

function showLoading(containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '<div class="loading">Загрузка данных...</div>';
}

async function loadUsers() {
    showLoading('users-list');
    const users = await apiCall('/users');
    if (users) {
        displayUsers(users);
    }
}

function displayUsers(users) {
    const container = document.getElementById('users-list');
    container.innerHTML = '';

    if (users.length === 0) {
        container.innerHTML = '<p>Пользователи не найдены</p>';
        return;
    }

    users.forEach(user => {
        const userDiv = document.createElement('div');
        userDiv.className = 'list-item';
        userDiv.innerHTML = `
            <h4>${user.username}</h4>
            <p><strong>Email:</strong> ${user.email}</p>
            <p><strong>ID:</strong> ${user.user_id}</p>
            <p><strong>Создан:</strong> ${new Date(user.created_at).toLocaleDateString('ru-RU')}</p>
        `;
        container.appendChild(userDiv);
    });
}

function showUserForm() {
    document.getElementById('user-form').style.display = 'block';
}

function hideUserForm() {
    document.getElementById('user-form').style.display = 'none';
    document.getElementById('userForm').reset();
}

document.getElementById('userForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    };

    const result = await apiCall('/users', 'POST', formData);
    if (result) {
        showSuccess('Пользователь создан успешно');
        hideUserForm();
        loadUsers();
    }
});

async function loadAccounts() {
    showLoading('accounts-list');
    const accounts = await apiCall('/accounts');
    if (accounts) {
        displayAccounts(accounts);
    }
}

function displayAccounts(accounts) {
    const container = document.getElementById('accounts-list');
    container.innerHTML = '';

    if (accounts.length === 0) {
        container.innerHTML = '<p>Счета не найдены</p>';
        return;
    }

    accounts.forEach(account => {
        const accountDiv = document.createElement('div');
        accountDiv.className = 'list-item';
        accountDiv.innerHTML = `
            <h4>${account.name}</h4>
            <p><strong>Тип:</strong> ${account.type}</p>
            <p><strong>Баланс:</strong> ${account.balance} ₽</p>
            <p><strong>ID:</strong> ${account.account_id}</p>
        `;
        container.appendChild(accountDiv);
    });
}

function showAccountForm() {
    document.getElementById('account-form').style.display = 'block';
}

function hideAccountForm() {
    document.getElementById('account-form').style.display = 'none';
    document.getElementById('accountForm').reset();
}

document.getElementById('accountForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        name: document.getElementById('accountName').value,
        type: document.getElementById('accountType').value,
        balance: parseFloat(document.getElementById('accountBalance').value)
    };

    const result = await apiCall('/accounts', 'POST', formData);
    if (result) {
        showSuccess('Счет создан успешно');
        hideAccountForm();
        loadAccounts();
    }
});

async function loadCategories() {
    showLoading('categories-list');
    const categories = await apiCall('/categories');
    if (categories) {
        displayCategories(categories);
    }
}

function displayCategories(categories) {
    const container = document.getElementById('categories-list');
    container.innerHTML = '';

    if (categories.length === 0) {
        container.innerHTML = '<p>Категории не найдены</p>';
        return;
    }

    categories.forEach(category => {
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'list-item';
        categoryDiv.innerHTML = `
            <h4>${category.name}</h4>
            <p><strong>Тип:</strong> ${category.type === 'income' ? 'Доход' : 'Расход'}</p>
            <p><strong>ID:</strong> ${category.category_id}</p>
        `;
        container.appendChild(categoryDiv);
    });
}

function showCategoryForm() {
    document.getElementById('category-form').style.display = 'block';
}

function hideCategoryForm() {
    document.getElementById('category-form').style.display = 'none';
    document.getElementById('categoryForm').reset();
}

document.getElementById('categoryForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        name: document.getElementById('categoryName').value,
        type: document.getElementById('categoryType').value
    };

    const result = await apiCall('/categories', 'POST', formData);
    if (result) {
        showSuccess('Категория создана успешно');
        hideCategoryForm();
        loadCategories();
    }
});

async function loadTransactions() {
    showLoading('transactions-list');
    const transactions = await apiCall('/transactions');
    if (transactions) {
        displayTransactions(transactions);
    }
}

async function displayTransactions(transactions) {
    const container = document.getElementById('transactions-list');
    container.innerHTML = '';

    if (transactions.length === 0) {
        container.innerHTML = '<p>Транзакции не найдены</p>';
        return;
    }

    const accounts = await apiCall('/accounts');
    const categories = await apiCall('/categories');

    const accountMap = {};
    const categoryMap = {};

    if (accounts) {
        accounts.forEach(account => {
            accountMap[account.account_id] = account.name;
        });
    }

    if (categories) {
        categories.forEach(category => {
            categoryMap[category.category_id] = category.name;
        });
    }

    transactions.forEach(transaction => {
        const transactionDiv = document.createElement('div');
        transactionDiv.className = 'list-item';
        transactionDiv.innerHTML = `
            <h4>Транзакция #${transaction.transaction_id}</h4>
            <p><strong>Сумма:</strong> ${transaction.amount} ₽</p>
            <p><strong>Счет:</strong> ${accountMap[transaction.account_id] || 'Неизвестно'}</p>
            <p><strong>Категория:</strong> ${categoryMap[transaction.category_id] || 'Неизвестно'}</p>
            <p><strong>Описание:</strong> ${transaction.description || 'Нет описания'}</p>
            <p><strong>Дата:</strong> ${new Date(transaction.transaction_date).toLocaleDateString('ru-RU')}</p>
            <div class="actions">
                <button class="edit-btn" onclick="editTransaction(${transaction.transaction_id})">Редактировать</button>
                <button class="delete-btn" onclick="deleteTransaction(${transaction.transaction_id})">Удалить</button>
            </div>
        `;
        container.appendChild(transactionDiv);
    });
}

function showTransactionForm() {
    document.getElementById('transaction-form').style.display = 'block';
}

function hideTransactionForm() {
    document.getElementById('transaction-form').style.display = 'none';
    document.getElementById('transactionForm').reset();
}

async function loadAccountsForSelect() {
    const accounts = await apiCall('/accounts');
    const select = document.getElementById('transactionAccount');
    const editSelect = document.getElementById('editTransactionAccount');

    if (accounts) {
        select.innerHTML = '<option value="">Выберите счет</option>';
        editSelect.innerHTML = '<option value="">Выберите счет</option>';

        accounts.forEach(account => {
            const option = document.createElement('option');
            option.value = account.account_id;
            option.textContent = account.name;
            select.appendChild(option);

            const editOption = document.createElement('option');
            editOption.value = account.account_id;
            editOption.textContent = account.name;
            editSelect.appendChild(editOption);
        });
    }
}

async function loadCategoriesForSelect() {
    const categories = await apiCall('/categories');
    const select = document.getElementById('transactionCategory');
    const editSelect = document.getElementById('editTransactionCategory');

    if (categories) {
        select.innerHTML = '<option value="">Выберите категорию</option>';
        editSelect.innerHTML = '<option value="">Выберите категорию</option>';

        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.category_id;
            option.textContent = category.name;
            select.appendChild(option);

            const editOption = document.createElement('option');
            editOption.value = category.category_id;
            editOption.textContent = category.name;
            editSelect.appendChild(editOption);
        });
    }
}

document.getElementById('transactionForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        account_id: parseInt(document.getElementById('transactionAccount').value),
        category_id: parseInt(document.getElementById('transactionCategory').value),
        amount: parseFloat(document.getElementById('transactionAmount').value),
        description: document.getElementById('transactionDescription').value,
        transaction_date: document.getElementById('transactionDate').value || new Date().toISOString().split('T')[0]
    };

    const result = await apiCall('/transactions', 'POST', formData);
    if (result) {
        showSuccess('Транзакция создана успешно');
        hideTransactionForm();
        loadTransactions();
    }
});

async function editTransaction(transactionId) {
    const transaction = await apiCall(`/transactions/${transactionId}`);
    if (transaction) {
        document.getElementById('editTransactionId').value = transaction.transaction_id;
        document.getElementById('editTransactionAccount').value = transaction.account_id;
        document.getElementById('editTransactionCategory').value = transaction.category_id;
        document.getElementById('editTransactionAmount').value = transaction.amount;
        document.getElementById('editTransactionDescription').value = transaction.description || '';
        document.getElementById('editTransactionDate').value = transaction.transaction_date;

        document.getElementById('transaction-edit').style.display = 'block';
    }
}

function hideTransactionEdit() {
    document.getElementById('transaction-edit').style.display = 'none';
    document.getElementById('transactionEditForm').reset();
}

document.getElementById('transactionEditForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const transactionId = document.getElementById('editTransactionId').value;
    const formData = {
        account_id: parseInt(document.getElementById('editTransactionAccount').value),
        category_id: parseInt(document.getElementById('editTransactionCategory').value),
        amount: parseFloat(document.getElementById('editTransactionAmount').value),
        description: document.getElementById('editTransactionDescription').value,
        transaction_date: document.getElementById('editTransactionDate').value
    };

    const result = await apiCall(`/transactions/${transactionId}`, 'PUT', formData);
    if (result) {
        showSuccess('Транзакция обновлена успешно');
        hideTransactionEdit();
        loadTransactions();
    }
});

async function deleteTransaction(transactionId) {
    if (confirm('Вы уверены, что хотите удалить эту транзакцию?')) {
        const result = await apiCall(`/transactions/${transactionId}`, 'DELETE');
        if (result) {
            showSuccess('Транзакция удалена успешно');
            loadTransactions();
        }
    }
}

async function loadBudgets() {
    showLoading('budgets-list');
    const budgets = await apiCall('/budgets');
    if (budgets) {
        displayBudgets(budgets);
    }
}

async function displayBudgets(budgets) {
    const container = document.getElementById('budgets-list');
    container.innerHTML = '';

    if (budgets.length === 0) {
        container.innerHTML = '<p>Бюджеты не найдены</p>';
        return;
    }

    const categories = await apiCall('/categories');
    const categoryMap = {};

    if (categories) {
        categories.forEach(category => {
            categoryMap[category.category_id] = category.name;
        });
    }

    budgets.forEach(budget => {
        const budgetDiv = document.createElement('div');
        budgetDiv.className = 'list-item';
        budgetDiv.innerHTML = `
            <h4>Бюджет #${budget.budget_id}</h4>
            <p><strong>Категория:</strong> ${categoryMap[budget.category_id] || 'Неизвестно'}</p>
            <p><strong>Лимит:</strong> ${budget.amount_limit} ₽</p>
            <p><strong>Период:</strong> ${new Date(budget.period_start).toLocaleDateString('ru-RU')} - ${new Date(budget.period_end).toLocaleDateString('ru-RU')}</p>
        `;
        container.appendChild(budgetDiv);
    });
}

function showBudgetForm() {
    document.getElementById('budget-form').style.display = 'block';
}

function hideBudgetForm() {
    document.getElementById('budget-form').style.display = 'none';
    document.getElementById('budgetForm').reset();
}

async function loadCategoriesForBudgetSelect() {
    const categories = await apiCall('/categories');
    const select = document.getElementById('budgetCategory');

    if (categories) {
        select.innerHTML = '<option value="">Выберите категорию</option>';

        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.category_id;
            option.textContent = category.name;
            select.appendChild(option);
        });
    }
}

document.getElementById('budgetForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        category_id: parseInt(document.getElementById('budgetCategory').value),
        amount_limit: parseFloat(document.getElementById('budgetAmount').value),
        period_start: document.getElementById('budgetStart').value,
        period_end: document.getElementById('budgetEnd').value
    };

    const result = await apiCall('/budgets', 'POST', formData);
    if (result) {
        showSuccess('Бюджет создан успешно');
        hideBudgetForm();
        loadBudgets();
    }
});

async function loadTransactionReport() {
    const transactions = await apiCall('/reports/transactions');
    if (transactions) {
        displayTransactionReport(transactions);
    }
}

function displayTransactionReport(transactions) {
    const container = document.getElementById('reports-content');
    container.innerHTML = '<h3>Отчет по транзакциям</h3>';

    if (transactions.length === 0) {
        container.innerHTML += '<p>Транзакции не найдены</p>';
        return;
    }

    const totalAmount = transactions.reduce((sum, t) => sum + parseFloat(t.amount), 0);
    const reportDiv = document.createElement('div');
    reportDiv.className = 'report-item';
    reportDiv.innerHTML = `
        <h4>Общая статистика</h4>
        <div class="stats">
            <div class="stat">
                <div class="label">Всего транзакций</div>
                <div class="value">${transactions.length}</div>
            </div>
            <div class="stat">
                <div class="label">Общая сумма</div>
                <div class="value">${totalAmount.toFixed(2)} ₽</div>
            </div>
        </div>
    `;
    container.appendChild(reportDiv);

    transactions.forEach(transaction => {
        const transactionDiv = document.createElement('div');
        transactionDiv.className = 'list-item';
        transactionDiv.innerHTML = `
            <h4>Транзакция #${transaction.transaction_id}</h4>
            <p><strong>Сумма:</strong> ${transaction.amount} ₽</p>
            <p><strong>Описание:</strong> ${transaction.description || 'Нет описания'}</p>
            <p><strong>Дата:</strong> ${new Date(transaction.transaction_date).toLocaleDateString('ru-RU')}</p>
        `;
        container.appendChild(transactionDiv);
    });
}

async function loadCategoryReport() {
    const report = await apiCall('/reports/categories');
    if (report) {
        displayCategoryReport(report);
    }
}

function displayCategoryReport(report) {
    const container = document.getElementById('reports-content');
    container.innerHTML = '<h3>Отчет по категориям</h3>';

    if (report.length === 0) {
        container.innerHTML += '<p>Данные по категориям не найдены</p>';
        return;
    }

    report.forEach(item => {
        const reportDiv = document.createElement('div');
        reportDiv.className = 'report-item';
        reportDiv.innerHTML = `
            <h4>${item.category}</h4>
            <p><strong>Тип:</strong> ${item.type === 'income' ? 'Доход' : 'Расход'}</p>
            <div class="stats">
                <div class="stat">
                    <div class="label">Количество транзакций</div>
                    <div class="value">${item.count}</div>
                </div>
                <div class="stat">
                    <div class="label">Общая сумма</div>
                    <div class="value">${item.total_amount.toFixed(2)} ₽</div>
                </div>
            </div>
        `;
        container.appendChild(reportDiv);
    });
}

document.addEventListener('DOMContentLoaded', function () {
    showSection('users');
});
