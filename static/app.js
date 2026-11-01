const state = { token: localStorage.getItem('focus_token'), username: localStorage.getItem('focus_user'), todos: [], filter: 'all', editing: null };
const $ = (id) => document.getElementById(id);
const api = async (path, options = {}) => {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(path, { ...options, headers });
  if (!response.ok) {
    let message = `Ошибка запроса (${response.status})`;
    try { const body = await response.json(); message = body.detail || message; } catch (_) {}
    if (response.status === 401) logout();
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
};
const show = (id, visible) => $(id).classList.toggle('hidden', !visible);
const toast = (message) => { $('toast').textContent = message; $('toast').classList.add('show'); setTimeout(() => $('toast').classList.remove('show'), 2200); };
function logout() { state.token = null; localStorage.removeItem('focus_token'); show('app-view', false); show('auth-view', true); }
function setAuthMode(register) {
  $('auth-title').textContent = register ? 'Создайте свой Focus' : 'Всё важное — под рукой';
  $('auth-subtitle').textContent = register ? 'Регистрация займёт меньше минуты.' : 'Войдите, чтобы управлять своими задачами.';
  $('email-field').classList.toggle('hidden', !register);
  $('auth-submit').textContent = register ? 'Зарегистрироваться' : 'Войти';
  $('auth-toggle').textContent = register ? 'У меня уже есть аккаунт' : 'Создать аккаунт';
  $('auth-form').dataset.register = register;
}
async function authenticate(event) {
  event.preventDefault(); $('auth-error').textContent = '';
  const register = $('auth-form').dataset.register === 'true';
  const username = $('auth-username').value.trim(), password = $('auth-password').value;
  try {
    if (register) {
      await api('/auth/create_user', { method: 'POST', body: JSON.stringify({ username, email: $('auth-email').value.trim() || null, password }) });
    }
    const result = await api('/auth/login-page', { method: 'POST', body: JSON.stringify({ username, email: null, password }) });
    state.token = result.access_token; state.username = username;
    localStorage.setItem('focus_token', state.token); localStorage.setItem('focus_user', username);
    show('auth-view', false); show('app-view', true); $('user-name').textContent = username; await loadTodos();
  } catch (error) { $('auth-error').textContent = error.message; }
}
async function loadTodos() {
  $('list-message').textContent = 'Загрузка…';
  try { const result = await api('/todos/todos'); state.todos = result['Your todos'] || []; }
  catch (error) { if (error.message.includes('(404)')) state.todos = []; else { $('list-message').textContent = error.message; return; } }
  render();
}
function render() {
  const query = $('search').value.toLowerCase();
  const filtered = state.todos.filter((todo) => (state.filter === 'all' || (state.filter === 'done' ? todo.done : !todo.done)) && `${todo.name} ${todo.description}`.toLowerCase().includes(query));
  $('total-count').textContent = state.todos.length; $('done-count').textContent = state.todos.filter((todo) => todo.done).length; $('open-count').textContent = state.todos.filter((todo) => !todo.done).length;
  $('list-message').textContent = filtered.length ? '' : (state.todos.length ? 'По вашему запросу ничего не найдено.' : 'Задач пока нет — добавьте первую.');
  $('task-list').innerHTML = filtered.map((todo) => `<article class="task ${todo.done ? 'done' : ''}"><input class="task-check" type="checkbox" data-action="toggle" data-id="${todo.user_task_number}" ${todo.done ? 'checked' : ''}><div><div class="task-name">${escapeHtml(todo.name)}</div><p class="task-description">${escapeHtml(todo.description)}</p>${(todo.tags || []).map((tag) => `<span class="tag ${tag.color}">${escapeHtml(tag.name)}</span>`).join('')}</div><div class="task-actions"><button class="icon-button" data-action="edit" data-id="${todo.user_task_number}" aria-label="Изменить">✎</button><button class="icon-button" data-action="delete" data-id="${todo.user_task_number}" aria-label="Удалить">×</button></div></article>`).join('');
}
function escapeHtml(value) { return String(value || '').replace(/[&<>"']/g, (char) => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#039;' }[char])); }
function openEditor(todo = null) { state.editing = todo; $('editor-title').textContent = todo ? 'Изменить задачу' : 'Новая задача'; $('task-name').value = todo?.name || ''; $('task-description').value = todo?.description || ''; $('task-importance').value = todo?.importance ?? 5; $('importance-value').textContent = $('task-importance').value; $('task-done').checked = Boolean(todo?.done); $('task-tag').value = todo?.tags?.[0]?.name || ''; $('task-color').value = todo?.tags?.[0]?.color || 'BLUE'; show('editor', true); $('task-name').focus(); }
async function saveTask(event) {
  event.preventDefault(); $('task-error').textContent = '';
  const payload = { todo_request: { name: $('task-name').value.trim(), description: $('task-description').value.trim(), done: $('task-done').checked, importance: Number($('task-importance').value), tags: [] }, tag: { name: $('task-tag').value.trim() || 'Общее', color: $('task-color').value } };
  try { await api(state.editing ? `/todos/change/item_id${state.editing.user_task_number}` : '/todos/addtodo', { method: state.editing ? 'PUT' : 'POST', body: JSON.stringify(payload) }); show('editor', false); toast(state.editing ? 'Задача обновлена' : 'Задача добавлена'); await loadTodos(); }
  catch (error) { $('task-error').textContent = error.message; }
}
async function handleTaskAction(event) {
  const control = event.target.closest('[data-action]'); if (!control) return;
  const todo = state.todos.find((item) => item.user_task_number === Number(control.dataset.id));
  try {
    if (control.dataset.action === 'edit') openEditor(todo);
    if (control.dataset.action === 'delete' && confirm('Удалить эту задачу?')) { await api(`/todos/delete/todo:${todo.user_task_number}`, { method: 'DELETE' }); toast('Задача удалена'); await loadTodos(); }
    if (control.dataset.action === 'toggle') { const payload = { todo_request: { name: todo.name, description: todo.description, done: control.checked, importance: todo.importance, tags: [] }, tag: { name: todo.tags?.[0]?.name || 'Общее', color: todo.tags?.[0]?.color || 'BLUE' } }; await api(`/todos/change/item_id${todo.user_task_number}`, { method: 'PUT', body: JSON.stringify(payload) }); await loadTodos(); }
  } catch (error) { toast(error.message); render(); }
}
$('auth-form').addEventListener('submit', authenticate); $('auth-toggle').addEventListener('click', () => setAuthMode($('auth-form').dataset.register !== 'true')); $('logout').addEventListener('click', logout); $('new-task').addEventListener('click', () => openEditor()); $('close-editor').addEventListener('click', () => show('editor', false)); $('task-form').addEventListener('submit', saveTask); $('task-list').addEventListener('click', handleTaskAction); $('task-list').addEventListener('change', handleTaskAction); $('search').addEventListener('input', render); $('task-importance').addEventListener('input', () => $('importance-value').textContent = $('task-importance').value); document.querySelectorAll('.filter').forEach((button) => button.addEventListener('click', () => { document.querySelector('.filter.active').classList.remove('active'); button.classList.add('active'); state.filter = button.dataset.filter; render(); }));
if (state.token) { show('auth-view', false); show('app-view', true); $('user-name').textContent = state.username || ''; loadTodos(); } else setAuthMode(false);
