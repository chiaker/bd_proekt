const API_BASE = 'http://localhost:8000';

let currentSection = 'users';

function getEntityId(obj) {
    return obj.id ?? obj.user_id ?? obj.account_id ?? obj.category_id ?? obj.transaction_id ?? obj.budget_id ?? null;
}

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
            // try to extract JSON error message
            let errMsg = `HTTP error! status: ${response.status}`;
            try {
                const errJson = await response.json();
                if (errJson.message) errMsg = errJson.message;
                else if (errJson.detail) errMsg = errJson.detail;
                else if (typeof errJson === 'string') errMsg = errJson;
            } catch (e) {
                // ignore JSON parse errors
            }
            throw new Error(errMsg);
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
            <p><strong>ID:</strong> ${getEntityId(user)}</p>
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
            <p><strong>ID:</strong> ${getEntityId(account)}</p>
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
            <p><strong>ID:</strong> ${getEntityId(category)}</p>
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
    const transfers = await apiCall('/transactions/ba');
    if (transactions || transfers) {
        displayAllTransactions(transactions || [], transfers || []);
    }
}

async function displayAllTransactions(transactions, transfers) {
    const container = document.getElementById('transactions-list');
    container.innerHTML = '';

    if ((!transactions || transactions.length === 0) && (!transfers || transfers.length === 0)) {
        container.innerHTML = '<p>Транзакции не найдены</p>';
        return;
    }

    const accounts = await apiCall('/accounts');
    const categories = await apiCall('/categories');

    const accountMap = {};
    const categoryMap = {};

    if (accounts) {
        accounts.forEach(account => {
            accountMap[getEntityId(account)] = account.name;
        });
    }

    if (categories) {
        categories.forEach(category => {
            categoryMap[getEntityId(category)] = category.name;
        });
    }

    // unify items and sort by date desc
    const unified = [];
    if (transactions) {
        transactions.forEach(transaction => unified.push({ _type: 'transaction', ...transaction }));
    }
    if (transfers) {
        transfers.forEach(t => unified.push({ _type: 'transfer', ...t }));
    }

    unified.sort((a, b) => new Date(b.transaction_date) - new Date(a.transaction_date));

    unified.forEach(item => {
        const transactionDiv = document.createElement('div');
        transactionDiv.className = 'list-item';
        if (item._type === 'transaction') {
            transactionDiv.innerHTML = `
                <h4>Транзакция #${getEntityId(item)}</h4>
                <p><strong>Сумма:</strong> ${item.amount} ₽</p>
                <p><strong>Счет:</strong> ${accountMap[item.account_id] || 'Неизвестно'}</p>
                <p><strong>Категория:</strong> ${categoryMap[item.category_id] || 'Неизвестно'}</p>
                <p><strong>Описание:</strong> ${item.description || 'Нет описания'}</p>
                <p><strong>Дата:</strong> ${new Date(item.transaction_date).toLocaleDateString('ru-RU')}</p>
                <div class="actions">
                    <button class="edit-btn" onclick="editTransaction(${getEntityId(item)})">Редактировать</button>
                    <button class="delete-btn" onclick="deleteTransaction(${getEntityId(item)})">Удалить</button>
                </div>
            `;
        } else {
            transactionDiv.innerHTML = `
                <h4>Перевод #${getEntityId(item)}</h4>
                <p><strong>Сумма:</strong> ${item.amount} ₽</p>
                <p><strong>От:</strong> ${accountMap[item.account_id_from] || 'Неизвестно'}</p>
                <p><strong>К:</strong> ${accountMap[item.account_id_to] || 'Неизвестно'}</p>
                <p><strong>Описание:</strong> ${item.description || 'Нет описания'}</p>
                <p><strong>Дата:</strong> ${new Date(item.transaction_date).toLocaleDateString('ru-RU')}</p>
                <div class="actions">
                    <button class="edit-btn" onclick="editTransfer(${getEntityId(item)})">Редактировать</button>
                    <button class="delete-btn" onclick="deleteTransfer(${getEntityId(item)})">Удалить</button>
                </div>
            `;
        }
        container.appendChild(transactionDiv);
    });
}

function showTransactionForm() {
    document.getElementById('transaction-form').style.display = 'block';
}

async function showTransferForm() {
    document.getElementById('transfer-form').style.display = 'block';
    // populate select options (re-use accounts select population)
    await loadAccountsForSelect();
    const fromSelect = document.getElementById('transferAccountFrom');
    const toSelect = document.getElementById('transferAccountTo');
    if (fromSelect && toSelect) {
        // copy values from transactionAccount options
        const src = document.getElementById('transactionAccount');
        fromSelect.innerHTML = '<option value="">Счет откуда</option>';
        toSelect.innerHTML = '<option value="">Счет куда</option>';
        for (let i = 0; i < src.options.length; i++) {
            const o = src.options[i];
            const option1 = document.createElement('option');
            option1.value = o.value;
            option1.textContent = o.textContent;
            fromSelect.appendChild(option1);

            const option2 = document.createElement('option');
            option2.value = o.value;
            option2.textContent = o.textContent;
            toSelect.appendChild(option2);
        }
    }
}

function hideTransferForm() {
    document.getElementById('transfer-form').style.display = 'none';
    document.getElementById('transferForm').reset();
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
            option.value = getEntityId(account);
            option.textContent = account.name;
            select.appendChild(option);

            const editOption = document.createElement('option');
            editOption.value = getEntityId(account);
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
            option.value = getEntityId(category);
            option.textContent = category.name;
            select.appendChild(option);

            const editOption = document.createElement('option');
            editOption.value = getEntityId(category);
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
        loadAccounts();
    }
});

document.getElementById('transferForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        account_id_from: parseInt(document.getElementById('transferAccountFrom').value),
        account_id_to: parseInt(document.getElementById('transferAccountTo').value),
        amount: parseFloat(document.getElementById('transferAmount').value),
        description: document.getElementById('transferDescription').value,
        transaction_date: document.getElementById('transferDate').value || new Date().toISOString().split('T')[0]
    };

    // Client-side validation
    if (!formData.account_id_from || !formData.account_id_to) {
        showError('Выберите счета отправления и получения');
        return;
    }
    if (formData.account_id_from === formData.account_id_to) {
        showError('Счета отправления и получения не должны совпадать');
        return;
    }
    if (!formData.amount || formData.amount <= 0) {
        showError('Введите корректную сумму перевода');
        return;
    }

    const result = await apiCall('/transactions/ba', 'POST', formData);
    if (result) {
        showSuccess('Перевод создан успешно');
        hideTransferForm();
        loadTransactions();
        loadAccounts();
    }
});

async function editTransaction(transactionId) {
    const transaction = await apiCall(`/transactions/${transactionId}`);
    if (transaction) {
        document.getElementById('editTransactionId').value = transaction.id;
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
        loadAccounts();
    }
});

async function deleteTransaction(transactionId) {
    if (confirm('Вы уверены, что хотите удалить эту транзакцию?')) {
        const result = await apiCall(`/transactions/${transactionId}`, 'DELETE');
        if (result) {
            showSuccess('Транзакция удалена успешно');
            loadTransactions();
            loadAccounts();
        }
    }
}

async function editTransfer(transferId) {
    const transfer = await apiCall(`/transactions/ba/${transferId}`);
    if (transfer) {
        // populate account selects
        await loadAccountsForSelect();
        const src = document.getElementById('transactionAccount');
        const from = document.getElementById('editTransferAccountFrom');
        const to = document.getElementById('editTransferAccountTo');

        from.innerHTML = '<option value="">Счет откуда</option>';
        to.innerHTML = '<option value="">Счет куда</option>';
        for (let i = 0; i < src.options.length; i++) {
            const o = src.options[i];
            const option1 = document.createElement('option'); option1.value = o.value; option1.textContent = o.textContent; from.appendChild(option1);
            const option2 = document.createElement('option'); option2.value = o.value; option2.textContent = o.textContent; to.appendChild(option2);
        }

        document.getElementById('editTransferId').value = transfer.id;
        document.getElementById('editTransferAccountFrom').value = transfer.account_id_from;
        document.getElementById('editTransferAccountTo').value = transfer.account_id_to;
        document.getElementById('editTransferAmount').value = transfer.amount;
        document.getElementById('editTransferDescription').value = transfer.description || '';
        document.getElementById('editTransferDate').value = transfer.transaction_date;

        document.getElementById('transfer-edit').style.display = 'block';
    }
}

function hideTransferEdit() {
    document.getElementById('transfer-edit').style.display = 'none';
    document.getElementById('transferEditForm').reset();
}

document.getElementById('transferEditForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const transferId = document.getElementById('editTransferId').value;
    const formData = {
        account_id_from: parseInt(document.getElementById('editTransferAccountFrom').value),
        account_id_to: parseInt(document.getElementById('editTransferAccountTo').value),
        amount: parseFloat(document.getElementById('editTransferAmount').value),
        description: document.getElementById('editTransferDescription').value,
        transaction_date: document.getElementById('editTransferDate').value
    };

    const result = await apiCall(`/transactions/ba/${transferId}`, 'PUT', formData);
    if (result) {
        showSuccess('Перевод обновлён успешно');
        hideTransferEdit();
        loadTransactions();
        loadAccounts();
    }
});

async function deleteTransfer(transferId) {
    if (confirm('Вы уверены, что хотите удалить этот перевод?')) {
        const result = await apiCall(`/transactions/ba/${transferId}`, 'DELETE');
        if (result) {
            showSuccess('Перевод удалён успешно');
            loadTransactions();
            loadAccounts();
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
            categoryMap[category.id] = category.name;
        });
    }

    budgets.forEach(budget => {
        const budgetDiv = document.createElement('div');
        budgetDiv.className = 'list-item';
        budgetDiv.innerHTML = `
            <h4>Бюджет #${budget.id}</h4>
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
            option.value = category.id;
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
            <h4>Транзакция #${transaction.id}</h4>
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
